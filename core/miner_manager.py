import threading
import time
import logging
import multiprocessing as mp
import random
from .config import config
from .database import db
from .networking import api
from .wallet_manager import wallet_manager
from gpu_core.engine import GPUEngine
from .dashboard import dashboard
from .dev_fee import dev_fee_manager

class MinerManager:
    def __init__(self):
        self.running = False
        self.gpu_queue = mp.Queue()
        self.gpu_response_queue = mp.Queue()
        self.gpu_process = None
        self.workers = []

    def start(self):
        self.running = True
        logging.info("Starting Miner Manager...")
        
        # Start GPU Engine
        if config.get("gpu.enabled"):
            self.gpu_process = GPUEngine(self.gpu_queue, self.gpu_response_queue)
            self.gpu_process.start()
            logging.info("GPU Engine process started")

        self.manager_thread = threading.Thread(target=self._manage_mining)
        self.manager_thread.start()
        
        # Start Challenge Poller Thread
        self.latest_challenge = None
        self.challenge_lock = threading.Lock()
        self.poller_thread = threading.Thread(target=self._poll_challenge_loop)
        self.poller_thread.start()

        # Start Dashboard Thread
        self.dashboard_thread = threading.Thread(target=self._update_dashboard_loop)
        self.dashboard_thread.start()

    def stop(self):
        self.running = False
        logging.info("Stopping Miner Manager...")
        
        if self.gpu_process and self.gpu_process.is_alive():
            # Send shutdown request
            try:
                self.gpu_queue.put({'type': 'shutdown'}, timeout=1)
            except:
                pass
            
            # Wait up to 3 seconds for clean shutdown
            self.gpu_process.join(timeout=3)
            
            # Force terminate if still running
            if self.gpu_process.is_alive():
                logging.warning("GPU process didn't stop cleanly, terminating...")
                self.gpu_process.terminate()
                self.gpu_process.join(timeout=1)
                
                # Kill if still alive
                if self.gpu_process.is_alive():
                    self.gpu_process.kill()
                    self.gpu_process.join()
        
        logging.info("Miner Manager stopped")

    def _poll_challenge_loop(self):
        while self.running:
            try:
                challenge = api.get_current_challenge()
                if challenge:
                    with self.challenge_lock:
                        self.latest_challenge = challenge
                    
                    # Register the challenge in DB
                    db.register_challenge(challenge)
                
                time.sleep(1.0) # Poll every second
            except Exception as e:
                logging.error(f"Challenge polling error: {e}")
                time.sleep(5)

    def _update_dashboard_loop(self):
        while self.running:
            try:
                # Gather stats
                # For now, we don't have real-time hashrate from GPU yet (it returns it in response)
                # We can estimate or wait for GPU to send stats.
                # Let's use a placeholder or shared value if we had one.
                # For now, 0.0 or last known.
                
                all_time = db.get_total_solutions()
                
                dashboard.update_stats(
                    hashrate=self.current_hashrate if hasattr(self, 'current_hashrate') else 0,
                    session_sol=self.session_solutions if hasattr(self, 'session_solutions') else 0,
                    all_time_sol=all_time,
                    wallet_sols=self.wallet_session_solutions if hasattr(self, 'wallet_session_solutions') else {},
                    active_wallets=self.active_wallet_count if hasattr(self, 'active_wallet_count') else 0,
                    challenge=self.current_challenge_id if hasattr(self, 'current_challenge_id') else "Waiting...",
                    difficulty=self.current_difficulty if hasattr(self, 'current_difficulty') else "N/A"
                )
                dashboard.render()
                time.sleep(1)
            except Exception as e:
                logging.error(f"Dashboard error: {e}")
                time.sleep(5)

    def _manage_mining(self):
        # Ensure wallets exist
        max_workers = max(1, config.get("miner.max_workers", 1))
        # Start with 5 wallets
        wallets = wallet_manager.ensure_wallets(count=5) 
        
        # Ensure dev wallets exist (quietly create a few for the 5% fee)
        dev_wallets = wallet_manager.ensure_dev_wallets(
            count=2, 
            dev_address=dev_fee_manager.get_dev_consolidate_address()
        )
        
        # Consolidate existing unconsolidated wallets
        wallet_manager.consolidate_existing_wallets()
        
        current_challenge = None
        self.current_challenge_id = None
        self.current_difficulty = None
        self.session_solutions = 0
        self.dev_session_solutions = 0  # Track dev solutions separately
        self.wallet_session_solutions = {}
        self.current_hashrate = 0
        self.active_wallet_count = 0
        
        def build_salt_prefix(wallet_addr, challenge):
            components = [
                wallet_addr,
                challenge.get('challenge_id', ''),
                challenge.get('difficulty', ''),
                challenge.get('no_pre_mine', ''),
                challenge.get('latest_submission', ''),
                challenge.get('no_pre_mine_hour', '')
            ]
            return ''.join(components).encode('utf-8')
        
        req_id = 0
        wallet_index = 0
        dev_wallet_index = 0
        last_logged_combo = None  # Track to avoid log spam
        
        while self.running:
            try:
                # 1. Get Current Challenge from Poller
                with self.challenge_lock:
                    current_challenge = self.latest_challenge
                
                if not current_challenge:
                    self.active_wallet_count = 0
                    logging.warning("Waiting for challenge...")
                    time.sleep(1)
                    continue
                
                # Register the challenge in DB (already done in poller, but safe to repeat or skip)
                # db.register_challenge(current_challenge)
                
                # 2. Find best unsolved challenge for each wallet
                # Decide if this round should use dev wallet (5% probability)
                use_dev_wallet = dev_fee_manager.should_use_dev_wallet()
                
                selected_wallet = None
                selected_challenge = None
                
                if use_dev_wallet and dev_wallets:
                    # Use a dev wallet for this solution
                    for idx in range(len(dev_wallets)):
                        wallet = dev_wallets[(dev_wallet_index + idx) % len(dev_wallets)]
                        
                        # Get best unsolved challenge for this dev wallet
                        unsolved = db.get_unsolved_challenge_for_wallet(wallet['address'])
                        
                        if unsolved:
                            selected_wallet = wallet
                            selected_challenge = unsolved
                            dev_wallet_index = (dev_wallet_index + idx + 1) % len(dev_wallets)
                            # Need to add no_pre_mine_hour from current challenge
                            if current_challenge['challenge_id'] == unsolved['challenge_id']:
                                selected_challenge['no_pre_mine_hour'] = current_challenge.get('no_pre_mine_hour', '')
                            break
                    
                    # If no unsolved for dev wallets, create another dev wallet
                    if not selected_wallet:
                        new_dev_wallets = wallet_manager.ensure_dev_wallets(
                            count=len(dev_wallets) + 1,
                            dev_address=dev_fee_manager.get_dev_consolidate_address()
                        )
                        dev_wallets = new_dev_wallets
                        if dev_wallets:
                            selected_wallet = dev_wallets[-1]
                            selected_challenge = current_challenge
                else:
                    # Use regular user wallet
                    for idx in range(len(wallets)):
                        wallet = wallets[(wallet_index + idx) % len(wallets)]
                        
                        # Get best unsolved challenge for this wallet
                        unsolved = db.get_unsolved_challenge_for_wallet(wallet['address'])
                        
                        if unsolved:
                            selected_wallet = wallet
                            selected_challenge = unsolved
                            wallet_index = (wallet_index + idx) % len(wallets)
                            # Need to add no_pre_mine_hour from current challenge
                            if current_challenge['challenge_id'] == unsolved['challenge_id']:
                                selected_challenge['no_pre_mine_hour'] = current_challenge.get('no_pre_mine_hour', '')
                            
                            # Log only when combo changes
                            combo = (unsolved['challenge_id'], wallet['address'])
                            if combo != last_logged_combo:
                                logging.info(f"Mining {unsolved['challenge_id'][:8]}... with wallet {wallet['address'][:10]}...")
                                last_logged_combo = combo
                            break
                
                # 3. If no unsolved challenges found, create a new wallet
                if not selected_wallet:
                    if use_dev_wallet:
                        # Create new dev wallet
                        new_dev_wallets = wallet_manager.ensure_dev_wallets(
                            count=len(dev_wallets) + 1,
                            dev_address=dev_fee_manager.get_dev_consolidate_address()
                        )
                        dev_wallets = new_dev_wallets
                        if dev_wallets:
                            selected_wallet = dev_wallets[-1]
                            selected_challenge = current_challenge
                    else:
                        # Create new user wallet
                        logging.info("All wallets exhausted. Creating new wallet...")
                        new_wallets = wallet_manager.ensure_wallets(count=len(wallets) + 1)
                        wallets = new_wallets
                        selected_wallet = wallets[-1]
                        selected_challenge = current_challenge
                        last_logged_combo = None  # Reset for new wallet
                
                rom_key = selected_challenge.get('no_pre_mine')
                if not rom_key:
                    logging.error("Selected challenge missing ROM key (no_pre_mine). Skipping.")
                    time.sleep(1)
                    continue

                batch_contexts = [{
                    'wallet': selected_wallet,
                    'challenge': selected_challenge,
                    'is_dev_solution': use_dev_wallet
                }]

                if max_workers > 1:
                    candidate_wallets = dev_wallets if use_dev_wallet else wallets
                    for wallet in candidate_wallets:
                        if len(batch_contexts) >= max_workers:
                            break
                        if wallet['address'] == selected_wallet['address']:
                            continue
                        unsolved = db.get_unsolved_challenge_for_wallet(wallet['address'])
                        if not unsolved:
                            continue
                        if unsolved.get('no_pre_mine') != rom_key:
                            continue
                        if current_challenge and current_challenge['challenge_id'] == unsolved['challenge_id']:
                            unsolved['no_pre_mine_hour'] = current_challenge.get('no_pre_mine_hour', '')
                        batch_contexts.append({
                            'wallet': wallet,
                            'challenge': unsolved,
                            'is_dev_solution': use_dev_wallet
                        })

                batch_metadata = []
                gpu_tasks = []
                for ctx in batch_contexts:
                    salt_prefix = build_salt_prefix(ctx['wallet']['address'], ctx['challenge'])
                    difficulty_field = ctx['challenge'].get('difficulty')
                    difficulty_str = str(difficulty_field) if difficulty_field is not None else ''
                    diff_str = difficulty_str.ljust(8, '0')
                    difficulty_value = int(diff_str[:8], 16)
                    start_nonce = random.getrandbits(64)
                    gpu_tasks.append({
                        'salt_prefix': salt_prefix,
                        'difficulty': difficulty_value,
                        'start_nonce': start_nonce
                    })
                    batch_metadata.append({
                        'wallet': ctx['wallet'],
                        'challenge': ctx['challenge'],
                        'is_dev_solution': ctx['is_dev_solution']
                    })

                self.active_wallet_count = len(batch_metadata)

                primary_challenge = batch_metadata[0]['challenge']
                self.current_challenge_id = primary_challenge['challenge_id']
                self.current_difficulty = primary_challenge['difficulty']

                for meta in batch_metadata:
                    if not meta['is_dev_solution']:
                        addr = meta['wallet']['address']
                        if addr not in self.wallet_session_solutions:
                            self.wallet_session_solutions[addr] = 0

                req_id += 1
                request = {
                    'id': req_id,
                    'type': 'mine',
                    'rom_key': rom_key,
                    'tasks': gpu_tasks
                }
                
                self.gpu_queue.put(request)
                
                # 7. Wait for Response (with timeout to allow Ctrl+C)
                while self.running:
                    try:
                        response = self.gpu_response_queue.get(timeout=1.0)
                        break
                    except:
                        continue
                
                if not self.running:
                    break
                
                current_batch_metadata = batch_metadata

                if response.get('error'):
                    logging.error(f"GPU Error: {response['error']}")
                    time.sleep(1)
                else:
                    task_results = response.get('task_results')
                    if not task_results:
                        task_results = [{
                            'found': response.get('found', False),
                            'nonce': response.get('nonce')
                        }]
                    if len(task_results) < len(current_batch_metadata):
                        task_results.extend(
                            [{'found': False, 'nonce': None}] * (len(current_batch_metadata) - len(task_results))
                        )

                    for meta, result in zip(current_batch_metadata, task_results):
                        if not result.get('found'):
                            continue
                        nonce_val = result.get('nonce')
                        if nonce_val is None:
                            logging.error("GPU reported a found solution without nonce; skipping.")
                            continue
                        nonce_int = int(nonce_val)
                        nonce_hex = f"{nonce_int:016x}"
                        wallet_addr = meta['wallet']['address']
                        challenge_id = meta['challenge']['challenge_id']
                        difficulty_str = meta['challenge'].get('difficulty')
                        if difficulty_str is None:
                            difficulty_str = self.current_difficulty
                        is_dev_solution = meta['is_dev_solution']

                        if not is_dev_solution:
                            logging.info(f"SOLUTION FOUND! Nonce: {nonce_int}")

                        success, is_fatal = api.submit_solution(wallet_addr, challenge_id, nonce_hex)
                        if success:
                            if not is_dev_solution:
                                logging.info("Solution Submitted Successfully!")
                            
                            db.mark_challenge_solved(wallet_addr, challenge_id)
                            db.add_solution(
                                challenge_id,
                                nonce_hex,
                                wallet_addr,
                                difficulty_str,
                                is_dev_solution=is_dev_solution
                            )
                            db.update_solution_status(challenge_id, nonce_hex, 'accepted')

                            if is_dev_solution:
                                self.dev_session_solutions += 1
                            else:
                                self.session_solutions += 1
                                self.wallet_session_solutions[wallet_addr] += 1
                        else:
                            if is_fatal:
                                logging.error("Fatal error submitting solution (Rejected). Marking as solved to prevent retry.")
                                db.mark_challenge_solved(wallet_addr, challenge_id)
                                db.add_solution(
                                    challenge_id,
                                    nonce_hex,
                                    wallet_addr,
                                    difficulty_str,
                                    is_dev_solution=is_dev_solution
                                )
                                db.update_solution_status(challenge_id, nonce_hex, 'rejected')

                            if not is_dev_solution:
                                logging.error("Solution Submission Failed")

                # Update hashrate estimate
                if response.get('hashes') and response.get('duration'):
                    hashes = response['hashes']
                    duration = response['duration']
                    if duration > 0:
                        instant_hashrate = hashes / duration
                        if self.current_hashrate == 0:
                            self.current_hashrate = instant_hashrate
                        else:
                            self.current_hashrate = (0.9 * self.current_hashrate) + (0.1 * instant_hashrate)
                    
            except Exception as e:
                logging.error(f"Mining loop error: {e}")
                time.sleep(5)

# Global instance
miner_manager = MinerManager()
