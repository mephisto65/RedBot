# Dockerfile complet pour LLM Pentesting API
FROM kalilinux/kali-rolling

# Mise à jour du système
RUN apt-get update && apt-get upgrade -y

# Installation des outils de pentesting et des packages Python
RUN apt-get install -y \
    # autres outils de base
    exploitdb \
    metasploit-framework \
    # Outils de reconnaissance et scanning
    nmap \
    masscan \
    dnsutils \
    whois \
    netcat-traditional \
    iputils-ping \
    net-tools \
    # Outils web
    gobuster \
    nikto \
    dirb \
    sqlmap \
    curl \
    wget \
    # Outils de cracking
    hydra \
    john \
    hashcat \
    # Outils réseau
    tcpdump \
    wireshark-common \
    aircrack-ng \
    # Outils système
    python3 \
    python3-pip \
    python3-venv \
    git \
    vim \
    && rm -rf /var/lib/apt/lists/*


RUN setcap cap_net_raw+ep /bin/ping
# Getting wordlists and SecLists

RUN mkdir /usr/share/wordlists
RUN mkdir /usr/share/wordlists/dirb
RUN mkdir /usr/share/wordlists/enumeration

RUN mv /usr/share/dirb/wordlists/*.txt /usr/share/wordlists/dirb/

RUN wget -O /usr/share/wordlists/rockyou.txt https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt

RUN wget -O /usr/share/wordlists/enumeration/directory_list_medium.txt https://raw.githubusercontent.com/danielmiessler/SecLists/refs/heads/master/Discovery/Web-Content/DirBuster-2007_directory-list-2.3-medium.txt
RUN wget -O /usr/share/wordlists/enumeration/subdomains-110000.txt https://raw.githubusercontent.com/danielmiessler/SecLists/refs/heads/master/Discovery/DNS/subdomains-top1million-110000.txt

# Getting privilege escalation module

RUN mkdir -p /home/pentest/linpeas
RUN wget https://github.com/carlospolop/PEASS-ng/releases/latest/download/linpeas.sh -O /home/pentest/linpeas/linpeas.sh
RUN chmod +x /home/pentest/linpeas/linpeas.sh

# Correction des permissions pour nmap (nécessaire pour les scans)
RUN chmod +s /usr/bin/nmap

# Création d'un utilisateur non-root pour la sécurité
RUN useradd -m -s /bin/bash pentest

# Création des répertoires de travail
RUN mkdir -p /home/pentest/workspace /home/pentest/results /home/pentest/api
RUN chown -R pentest:pentest /home/pentest

# Copie des fichiers de l'API dans le container
COPY secure_command_executor.py /home/pentest/api/
COPY api_server.py /home/pentest/api/
COPY requirements.txt /home/pentest/api/

# Attribution des bonnes permissions aux fichiers
RUN chown -R pentest:pentest /home/pentest/api
RUN chmod +x /home/pentest/api/api_server.py

# Basculement vers l'utilisateur non-root
USER pentest

# Configuration de l'environnement virtuel Python
WORKDIR /home/pentest/api
RUN python3 -m venv myenv && \
    myenv/bin/pip install --upgrade pip && \
    myenv/bin/pip install -r requirements.txt

# Configuration des variables d'environnement
ENV PYTHONPATH=/home/pentest
ENV FLASK_APP=api_server.py
ENV FLASK_ENV=production
ENV PATH="/home/pentest/api/myenv/bin:$PATH"

# Retour au répertoire de travail principal
WORKDIR /home/pentest

# Exposition du port pour l'API
EXPOSE 8080

# Health check pour vérifier que l'API fonctionne
HEALTHCHECK --interval=300s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Commande de démarrage de l'API
CMD ["/home/pentest/api/myenv/bin/python", "/home/pentest/api/api_server.py"]