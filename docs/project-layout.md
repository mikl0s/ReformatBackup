reformatbackup/
├── src/
│   ├── __init__.py
│   ├── main.py         # Entry point, <500 lines
│   ├── scan.py        # App scanning logic
│   ├── backup.py      # Backup functionality
│   ├── restore.py     # Restore functionality
│   ├── utils.py       # Helpers (e.g., JSON, 7zip)
│   └── routes.py      # Flask routes
├── templates/
│   ├── base.html      # Base template with theme toggle
│   ├── index.html     # Main app list view
│   ├── backup.html    # Backup interface
│   └── restore.html   # Restore interface
├── static/
│   ├── css/
│   │   └── styles.css # Theme definitions
│   └── js/
│       └── app.js     # UI interactions
├── pyproject.toml     # Package config
└── README.md