import subprocess
import shlex
import time
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

class CommandCategory(Enum):
    RECONNAISSANCE = "reconnaissance"
    SCANNING = "scanning" 
    ENUMERATION = "enumeration"
    EXPLOITATION = "exploitation"
    POST_EXPLOITATION = "post_exploitation"
    REPORTING = "reporting"
    BASIC = "basic"

@dataclass
class CommandResult:
    success: bool
    stdout: str
    stderr: str
    return_code: int
    execution_time: float
    command: str
    category: CommandCategory

class SecureCommandExecutor:
    def __init__(self, timeout: int = 300, max_output_size: int = None):
        self.timeout = timeout
        self.max_output_size = max_output_size
        self.logger = self._setup_logging()
        
        # Liste blanche des commandes autorisées - mise à jour avec tous les outils du Dockerfile
        self.allowed_commands = {
            # Outils de reconnaissance et scanning (du Dockerfile)
            "nmap": CommandCategory.RECONNAISSANCE,
            "masscan": CommandCategory.SCANNING,
            "ping": CommandCategory.RECONNAISSANCE,
            "dig": CommandCategory.RECONNAISSANCE,
            "nslookup": CommandCategory.RECONNAISSANCE,
            "host": CommandCategory.RECONNAISSANCE,
            "whois": CommandCategory.RECONNAISSANCE,
            "netcat": CommandCategory.RECONNAISSANCE,
            "nc": CommandCategory.RECONNAISSANCE,
            "netcat-traditional": CommandCategory.RECONNAISSANCE,
            "searchsploit": CommandCategory.EXPLOITATION,
            
            # Outils web (du Dockerfile)
            "gobuster": CommandCategory.ENUMERATION,
            "nikto": CommandCategory.ENUMERATION,
            "dirb": CommandCategory.ENUMERATION,
            "sqlmap": CommandCategory.EXPLOITATION,
            "xsser": CommandCategory.EXPLOITATION,
            "curl": CommandCategory.ENUMERATION,
            "wget": CommandCategory.ENUMERATION,
            
            # Outils de cracking (du Dockerfile)
            "hydra": CommandCategory.EXPLOITATION,
            "john": CommandCategory.EXPLOITATION,
            "hashcat": CommandCategory.EXPLOITATION,
            
            # Outils réseau (du Dockerfile)
            "tcpdump": CommandCategory.RECONNAISSANCE,
            "wireshark": CommandCategory.RECONNAISSANCE,
            "tshark": CommandCategory.RECONNAISSANCE,
            "aircrack-ng": CommandCategory.EXPLOITATION,
            "airmon-ng": CommandCategory.RECONNAISSANCE,
            "airodump-ng": CommandCategory.RECONNAISSANCE,
            "aireplay-ng": CommandCategory.EXPLOITATION,
            
            # Commandes système de base disponibles dans Kali
            "whoami": CommandCategory.BASIC,
            "id": CommandCategory.BASIC,
            "pwd": CommandCategory.BASIC,
            "ls": CommandCategory.BASIC,
            "cat": CommandCategory.BASIC,
            "head": CommandCategory.BASIC,
            "tail": CommandCategory.BASIC,
            "grep": CommandCategory.BASIC,
            "awk": CommandCategory.BASIC,
            "sed": CommandCategory.BASIC,
            "find": CommandCategory.BASIC,
            "which": CommandCategory.BASIC,
            "whereis": CommandCategory.BASIC,
            "file": CommandCategory.BASIC,
            "stat": CommandCategory.BASIC,
            "du": CommandCategory.BASIC,
            "df": CommandCategory.BASIC,
            "ps": CommandCategory.BASIC,
            "top": CommandCategory.BASIC,
            "uname": CommandCategory.BASIC,
            "hostname": CommandCategory.BASIC,
            "date": CommandCategory.BASIC,
            "uptime": CommandCategory.BASIC,
            "who": CommandCategory.BASIC,
            "w": CommandCategory.BASIC,
            "echo": CommandCategory.BASIC,
            "printf": CommandCategory.BASIC,
            "wc": CommandCategory.BASIC,
            "sort": CommandCategory.BASIC,
            "uniq": CommandCategory.BASIC,
            "cut": CommandCategory.BASIC,
            "tr": CommandCategory.BASIC,
            "free": CommandCategory.BASIC,
            "netstat": CommandCategory.RECONNAISSANCE,
            "ss": CommandCategory.RECONNAISSANCE,
            "lsof": CommandCategory.BASIC,
            "ifconfig": CommandCategory.BASIC,
            "ip": CommandCategory.BASIC,
            "route": CommandCategory.BASIC,
            
            # Outils réseau additionnels
            "traceroute": CommandCategory.RECONNAISSANCE,
            "tracepath": CommandCategory.RECONNAISSANCE,
            "mtr": CommandCategory.RECONNAISSANCE,
            "arping": CommandCategory.RECONNAISSANCE,
            "hping3": CommandCategory.RECONNAISSANCE,
            "fping": CommandCategory.RECONNAISSANCE,
            "telnet": CommandCategory.RECONNAISSANCE,
            "ssh": CommandCategory.BASIC,
            "scp": CommandCategory.BASIC,
            
            # Outils d'énumération
            "enum4linux": CommandCategory.ENUMERATION,
            "nbtscan": CommandCategory.ENUMERATION,
            "smbclient": CommandCategory.ENUMERATION,
            "rpcclient": CommandCategory.ENUMERATION,
            "showmount": CommandCategory.ENUMERATION,
            "rpcinfo": CommandCategory.ENUMERATION,
            "snmpwalk": CommandCategory.ENUMERATION,
            "onesixtyone": CommandCategory.ENUMERATION,
            
            # Outils web additionnels courants dans Kali
            "wfuzz": CommandCategory.ENUMERATION,
            "ffuf": CommandCategory.ENUMERATION,
            "whatweb": CommandCategory.ENUMERATION,
            "wafw00f": CommandCategory.ENUMERATION,
            "wpscan": CommandCategory.ENUMERATION,
            
            # Outils de cracking additionnels
            "medusa": CommandCategory.EXPLOITATION,
            "ncrack": CommandCategory.EXPLOITATION,
            "crunch": CommandCategory.EXPLOITATION,
            "cewl": CommandCategory.ENUMERATION,
            "hashid": CommandCategory.BASIC,
            
            # Outils d'analyse
            "strings": CommandCategory.BASIC,
            "hexdump": CommandCategory.BASIC,
            "xxd": CommandCategory.BASIC,
            "od": CommandCategory.BASIC,
            "binwalk": CommandCategory.BASIC,
            
            # Git et vim (installés dans le Dockerfile)
            "git": CommandCategory.BASIC,
            "vim": CommandCategory.BASIC,
            "vi": CommandCategory.BASIC,
            "nano": CommandCategory.BASIC,
            
            # Python (installé dans le Dockerfile)
            "python3": CommandCategory.BASIC,
            "pip": CommandCategory.BASIC,
            "pip3": CommandCategory.BASIC
        }
        
        # Commandes interdites
        self.forbidden_commands = {
            "rm", "rmdir", "del", "format", "fdisk", "mkfs",
            "dd", "shred", "chmod", "chown", "su", "sudo",
            "passwd", "useradd", "userdel", "reboot", "shutdown"
        }
    
    def _setup_logging(self):
        logger = logging.getLogger("SecureCommandExecutor")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _validate_command(self, command: str) -> Tuple[bool, str, CommandCategory]:
        if not command or not command.strip():
            return False, "Commande vide", None
        
        try:
            parsed = shlex.split(command)
        except ValueError as e:
            return False, f"Erreur de parsing: {e}", None
        
        if not parsed:
            return False, "Commande vide après parsing", None
        
        base_command = parsed[0].split('/')[-1]
        
        if base_command in self.forbidden_commands:
            return False, f"Commande interdite: {base_command}", None
        
        if base_command not in self.allowed_commands:
            return False, f"Commande non autorisée: {base_command}", None
        
        # Vérifications de patterns dangereux
        dangerous_patterns = ["&&", "||", ";", "|", ">", ">>", "<", "`", "$("]
        for pattern in dangerous_patterns:
            if pattern in command:
                return False, f"Pattern dangereux détecté: {pattern}", None
        
        category = self.allowed_commands[base_command]
        return True, "Commande validée", category
    
    def execute_command(self, command: str, working_dir: Optional[str] = None) -> CommandResult:
        start_time = time.time()
        
        is_valid, reason, category = self._validate_command(command)
        if not is_valid:
            self.logger.warning(f"Commande refusée: {command} - Raison: {reason}")
            return CommandResult(
                success=False,
                stdout="",
                stderr=f"Commande refusée: {reason}",
                return_code=-1,
                execution_time=0,
                command=command,
                category=category
            )
        
        self.logger.info(f"Exécution de la commande [{category.value}]: {command}")
        
        # Définir le répertoire de travail
        if working_dir and os.path.exists(working_dir):
            cwd = working_dir
        else:
            cwd = "/home/pentest/workspace"
            # Créer le répertoire s'il n'existe pas
            if not os.path.exists(cwd):
                try:
                    os.makedirs(cwd, exist_ok=True)
                except Exception:
                    cwd = "/home/pentest"
        
        try:
            process = subprocess.Popen(
                shlex.split(command),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL,
                cwd=cwd,
                text=True
            )
            
            try:
                stdout, stderr = process.communicate(timeout=self.timeout)
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                return CommandResult(
                    success=False,
                    stdout=stdout if stdout else "",
                    stderr=f"Timeout après {self.timeout}s",
                    return_code=-1,
                    execution_time=time.time() - start_time,
                    command=command,
                    category=category
                )
            
            execution_time = time.time() - start_time
            success = process.returncode == 0
            
            self.logger.info(f"Commande terminée - Code retour: {process.returncode}")
            
            return CommandResult(
                success=success,
                stdout=stdout or "",
                stderr=stderr or "",
                return_code=process.returncode,
                execution_time=execution_time,
                command=command,
                category=category
            )
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'exécution: {e}")
            return CommandResult(
                success=False,
                stdout="",
                stderr=f"Erreur d'exécution: {str(e)}",
                return_code=-1,
                execution_time=time.time() - start_time,
                command=command,
                category=category
            )
    
    def get_allowed_commands(self) -> Dict[str, str]:
        return {cmd: cat.value for cmd, cat in self.allowed_commands.items()}
    
    def execute_background_command(self, command):
        start_time = time.time()
        cwd = "/home/pentest/workspace"
        
        # Validation existante
        is_valid, reason, category = self._validate_command(command)
        if not is_valid:
            self.logger.warning(f"Commande refusée: {command} - Raison: {reason}")
            return CommandResult(
                success=False,
                stdout="",
                stderr=f"Commande refusée: {reason}",
                return_code=-1,
                execution_time=0,
                command=command,
                category=category,
            ), -1

        self.logger.info(f"Exécution de la commande [{category.value}]: {command}")
        
        try:
            process = subprocess.Popen(
                shlex.split(command),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL,
                cwd=cwd,
                text=True
            )
            
            # Attendre un court moment pour détecter les erreurs immédiates
            time.sleep(0.1)
            poll_result = process.poll()
            
            if poll_result is not None and poll_result != 0:
                # Le processus s'est terminé rapidement avec une erreur
                stdout, stderr = process.communicate()
                return CommandResult(
                    success=False,
                    stdout=stdout,
                    stderr=stderr,
                    return_code=poll_result,
                    execution_time=time.time() - start_time,
                    command=command,
                    category=category,
                ), -1
                
        except FileNotFoundError:
            error_msg = f"Commande introuvable: {command.split()[0]}"
            self.logger.error(error_msg)
            return CommandResult(
                success=False,
                stdout="",
                stderr=error_msg,
                return_code=-1,
                execution_time=time.time() - start_time,
                command=command,
                category=category,
            ), -1
            
        except PermissionError:
            error_msg = f"Permission refusée pour: {command}"
            self.logger.error(error_msg)
            return CommandResult(
                success=False,
                stdout="",
                stderr=error_msg,
                return_code=-1,
                execution_time=time.time() - start_time,
                command=command,
                category=category,
            ), -1
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'exécution: {e}")
            return CommandResult(
                success=False,
                stdout="",
                stderr=f"Erreur d'exécution: {str(e)}",
                return_code=-1,
                execution_time=time.time() - start_time,
                command=command,
                category=category,
            ), -1

        pid = process.pid
        self.logger.info(f"Commande lancée en arrière-plan avec PID: {pid}")
        
        result = CommandResult(
            success=True,
            stdout="",
            stderr="",
            return_code=0,
            execution_time=time.time() - start_time,
            command=command,
            category=category,
        )
        
        return result, pid, process