# WelVision - AI-Powered Industrial Inspection System

WelVision is a comprehensive AI-powered quality inspection system designed for industrial manufacturing environments. It provides automated defect detection using computer vision and machine learning technologies.

## Features

### 🔍 **Dual AI Model Support**
- **OD Model**: Detects 7 defect types (Rust, Dent, Spherical Mark, Damage, Flat Line, Damage on End, Roller)
- **BigFace Model**: Specialized detection for 4 critical defects (Rust, Dent, Damage, Roller)
- **Configurable Confidence Thresholds**: Adjustable sensitivity for each defect type

### 📊 **Comprehensive Management System**
- **Real-time Inspection**: Live camera feed with instant defect detection
- **Threshold Management**: Intuitive interface for adjusting detection sensitivity
- **User Management**: Multi-user support with authentication and role-based access
- **Data Analytics**: Inspection history, statistics, and reporting
- **Model Management**: Easy switching between different AI models

### 🗄️ **Advanced Tracking & Audit**
- **Threshold History**: Complete audit trail of all threshold changes
- **Employee Attribution**: Track who made what changes and when
- **Database Integration**: MySQL backend for reliable data storage
- **Export Capabilities**: Excel export for analysis and reporting

## Quick Start

### Prerequisites
- Python 3.7+
- MySQL Server
- Webcam or industrial camera
- NVIDIA GPU (recommended for optimal performance)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/welvision.git
cd welvision
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Database Setup**
- Install MySQL Server
- Create database `welvision_db`
- Configure connection in `config.py`

4. **Model Setup**
- Create `models/` directory
- Add your trained YOLO model files:
  - `models/od/your_od_model.pt`
  - `models/bigface/your_bf_model.pt`

5. **Run the application**
```bash
python main.py
```

## Configuration

### Database Configuration
Edit `config.py` to configure your MySQL connection:
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'welvision_db'
}
```

### Model Configuration
Update model paths in the application settings or directly in the configuration files.

## Usage

### 1. **User Authentication**
- Launch the application
- Log in with your credentials
- First-time setup requires admin account creation

### 2. **Model Management**
- Navigate to Model Management tab
- Select and configure OD/BigFace models
- Set detection thresholds for each defect type

### 3. **Live Inspection**
- Go to Inference tab
- Connect camera and start inspection
- Monitor real-time detection results
- Review and save inspection data

### 4. **Settings & Configuration**
- Access Settings tab for threshold adjustments
- View threshold history and audit trails
- Manage user accounts and permissions

### 5. **Data Analysis**
- Check System Status for performance metrics
- Export inspection data for further analysis
- Generate reports and statistics

## Project Structure

```
welvision/
├── main.py                     # Main application entry point
├── database.py                 # Database operations and management
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
│
├── UI Modules/
│   ├── inference_tab.py        # Live inspection interface
│   ├── model_management_tab.py # Model configuration
│   ├── model_preview_tab.py    # Model testing and preview
│   ├── settings_tab.py         # Settings and thresholds
│   ├── user_management_tab.py  # User account management
│   ├── data_tab.py            # Data viewing and export
│   ├── diagnosis_tab.py       # System diagnostics
│   └── system_check_tab.py    # System status monitoring
│
├── Authentication/
│   ├── password_manager.py     # Password management
│   └── password_cli.py         # Command-line password tools
│
├── Documentation/
│   ├── README.md                      # This file
│   ├── PASSWORD_SYSTEM_GUIDE.md       # Password system documentation
│   ├── THRESHOLD_TRACKING_README.md   # Threshold tracking documentation
│   ├── MySQL_Setup_Guide.md           # Database setup guide
│   └── WelVision_Application_Documentation.pdf
│
└── Utilities/
    ├── utils.py                # Utility functions
    └── generate_documentation.py # Documentation generator
```

## Security Features

- **Secure Authentication**: Encrypted password storage with bcrypt
- **Session Management**: Secure session handling with unique IDs
- **Audit Trails**: Complete logging of user actions and changes
- **Role-Based Access**: Different permission levels for users

## Database Schema

The system uses MySQL with the following key tables:
- `users` - User authentication and profile data
- `od_threshold_history` - OD model threshold change history
- `bigface_threshold_history` - BigFace model threshold change history
- `current_thresholds` - Latest threshold configurations
- `inspection_data` - Inspection results and statistics

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## Support & Documentation

- **Password System**: See `PASSWORD_SYSTEM_GUIDE.md`
- **Threshold Tracking**: See `THRESHOLD_TRACKING_README.md`
- **Database Setup**: See `MySQL_Setup_Guide.md`
- **Full Documentation**: See `WelVision_Application_Documentation.pdf`

## License

This project is proprietary software. All rights reserved.

## Contact

For support and inquiries, please contact your system administrator.

---

*WelVision - Precision through AI-powered inspection* 