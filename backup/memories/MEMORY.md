The user's server inventory note is stored at /home/agas/Hermes/home-server/ubuntu-server-inventory.md.
§
Hermes backup: github.com/agassparkle/hermes-agent-backup-wacu. Clone: ~/Hermes/hermes-agent-backup-wacu/. Skill: hermes-backup-restore.
§
Cloud servers: oracle-hermes (130.61.122.103) + oracle-foundry (141.144.205.247). hermes: SSH Hermes.key, Syncthing, jack-vault, iptables via netfilter-persistent. foundry: SSH agassparkle.key, Foundry VTT PM2 :30000/:30001, Caddy :80/:443, agassparkle.ddns.net, Forbidden Lands modules, ARM64, no Syncthing. Keys dir: /mnt/sda2/UBuntu_Backup/Oracle Cloud  Keys/ (double space).
§
Forbidden Lands: [[Resources/forbidden-lands-dice]]. d6+d8+d10+d12. Success=6, bane=1.
§
User's canonical Shield entity is media_player.android_tv_192_168_1_62, friendly_name Shield.
§
Pill reminder: [[Areas/home-assistant/pill-reminder]]. Webhook pill-reminder2, secret pill-secret-123. input_boolean ile günde 1 kere. Detay vault'ta.
§
User expects me to follow config files exactly without overriding settings (e.g., don't pass --webui-port if config already defines it). User gets frustrated when I make assumptions instead of checking actual config first.
§
Google OAuth: [[Resources/google-workspace-oauth]]. Token ~/.hermes/google_token.json. Proje "alpozben" Testing modunda.
§
Telegram pitfall: long tables/prompts truncate mid-sentence. Keep outputs compact; verify table blocks fully delivered before claiming a step done. User flagged this twice.
§
Gateway restart: dışarıdan yapılmalı. [[Wiki/hermes-gateway-restart]].
§
HA pitfalls: [[Wiki/home-assistant-pitfalls]]. duplicate automation key + shell_command restart.
§
wacu vault: /mnt/sda2/Obsidian Vaults/wacu/ — GitHub: agassparkle/wacu-vault. Syncthing sync. Git+push çalışıyor. Cron 5e542d49ade3: 23:00 TRT auto-push. AGENTS.md rules. Separate personal vault /mnt/sda2/Obsidian Vaults/.
§
Never give time estimates ("5 saniyelik iş", "5 dakika", etc.). User corrected this twice in one session — strong reaction. Just do the work without predicting how long it will take.
§
When sharing files (HTML diagrams, exports, etc.), save them to /mnt/sda2/Bot_File_Shares/ — the user's designated file share directory.
§
oracle-foundry (141.144.205.247): ARM64 Ubuntu 22.04, up 36 days. Runs Foundry VTT (2 PM2 instances on :30000/:30001), Caddy reverse proxy (:80/:443), agassparkle.ddns.net. Forbidden Lands modules installed. SSH key: agassparkle.key. No Syncthing installed. ICMP blocked, SSH on port 22 open.
§
Cloud server oracle-bijou: IP 130.61.208.84, hostname bijou, ARM64 Ubuntu 24.04 (Oracle kernel 6.17), 96GB disk, 11GB RAM. SSH key: Bijou.key at /mnt/sda2/UBuntu_Backup/Oracle Cloud  Keys/. User: ubuntu. Hermes v0.17.0 installed at ~/.hermes/hermes-agent/. PATH set in .bashrc. No Docker, no services yet.