#!/usr/bin/env python3
"""
WelVision Application Documentation Generator
Generates a comprehensive PDF documentation of UI components and backend functionalities
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
import os

def create_documentation():
    """Generate comprehensive WelVision application documentation"""
    
    # Create PDF document
    doc = SimpleDocTemplate(
        "WelVision_Application_Documentation.pdf",
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18
    )
    
    # Get default styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceBefore=20,
        spaceAfter=12,
        textColor=colors.darkblue
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=14,
        spaceBefore=15,
        spaceAfter=8,
        textColor=colors.darkgreen
    )
    
    # Story elements
    story = []
    
    # Title Page
    story.append(Paragraph("WelVision Application", title_style))
    story.append(Paragraph("Complete UI & Backend Documentation", styles['Heading2']))
    story.append(Spacer(1, 0.5*inch))
    
    # Application overview
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
    story.append(Paragraph("Version: 1.0", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Executive Summary
    story.append(Paragraph("Executive Summary", heading_style))
    summary_text = """
    WelVision is a comprehensive industrial vision inspection application built with Python and Tkinter. 
    The application provides advanced computer vision capabilities for quality control, user management, 
    and real-time camera monitoring. It features a robust authentication system, role-based access control, 
    and enterprise-grade security measures.
    """
    story.append(Paragraph(summary_text, styles['Normal']))
    story.append(PageBreak())
    
    # Application Architecture
    story.append(Paragraph("1. Application Architecture", heading_style))
    
    story.append(Paragraph("1.1 Technology Stack", subheading_style))
    tech_data = [
        ['Component', 'Technology', 'Purpose'],
        ['GUI Framework', 'Tkinter with ttk', 'Cross-platform desktop interface'],
        ['Computer Vision', 'OpenCV + YOLO', 'Object detection and image processing'],
        ['Database', 'MySQL', 'Data persistence and user management'],
        ['Authentication', 'SHA-256 + Salt', 'Secure password hashing'],
        ['Programming Language', 'Python 3.13', 'Core application development'],
        ['Image Processing', 'PIL/Pillow', 'Image manipulation and display']
    ]
    
    tech_table = Table(tech_data, colWidths=[2*inch, 2*inch, 2.5*inch])
    tech_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(tech_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Authentication System
    story.append(Paragraph("2. Authentication System", heading_style))
    
    story.append(Paragraph("2.1 Login Interface", subheading_style))
    login_features = """
    • Clean, professional login window with company branding
    • Email and password input fields with validation
    • Secure password masking
    • Account lockout protection after failed attempts
    • Role-based redirection after successful authentication
    • Real-time validation feedback
    """
    story.append(Paragraph(login_features, styles['Normal']))
    
    story.append(Paragraph("2.2 Security Features", subheading_style))
    security_features = """
    • SHA-256 password hashing with unique salt per user
    • Account lockout after 5 failed login attempts
    • Session management and automatic logout
    • Role-based access control (User, Admin, Super Admin)
    • Audit logging for all authentication events
    • Input sanitization to prevent SQL injection
    """
    story.append(Paragraph(security_features, styles['Normal']))
    
    story.append(Paragraph("2.3 User Roles", subheading_style))
    roles_data = [
        ['Role', 'Permissions', 'Access Level'],
        ['User', 'View cameras, basic operations', 'Limited'],
        ['Admin', 'User management, advanced features', 'Extended'],
        ['Super Admin', 'Full system access, user creation', 'Complete']
    ]
    
    roles_table = Table(roles_data, colWidths=[1.5*inch, 3*inch, 1.5*inch])
    roles_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(roles_table)
    story.append(PageBreak())
    
    # Main Application Interface
    story.append(Paragraph("3. Main Application Interface", heading_style))
    
    story.append(Paragraph("3.1 Application Layout", subheading_style))
    layout_description = """
    The main application uses a tabbed interface design with a professional dark theme. 
    The interface is optimized for industrial environments with high contrast and clear visibility. 
    Navigation is intuitive with role-based tab visibility.
    """
    story.append(Paragraph(layout_description, styles['Normal']))
    
    # Tab Documentation
    story.append(Paragraph("3.2 Application Tabs", subheading_style))
    
    # Camera Tab
    story.append(Paragraph("📹 Camera Tab", subheading_style))
    camera_features = """
    <b>Frontend Features:</b>
    • Dual camera feed display (Object Detection and Barcode)
    • Real-time YOLO object detection overlay
    • Live camera status indicators
    • Image capture and save functionality
    • Detection results display panel
    
    <b>Backend Integration:</b>
    • OpenCV camera interface with error handling
    • YOLO model loading and inference
    • Real-time frame processing in separate threads
    • Automatic camera reconnection on failure
    • Image preprocessing and enhancement
    """
    story.append(Paragraph(camera_features, styles['Normal']))
    
    # Inspection Tab
    story.append(Paragraph("🔍 Inspection Tab", subheading_style))
    inspection_features = """
    <b>Frontend Features:</b>
    • Product selection via dropdown menu
    • Manual image upload and processing
    • Results visualization with annotations
    • Quality metrics display
    • Pass/Fail determination interface
    
    <b>Backend Integration:</b>
    • Image analysis algorithms
    • Product specification database lookup
    • Quality threshold comparison
    • Automated report generation
    • Historical data logging
    """
    story.append(Paragraph(inspection_features, styles['Normal']))
    
    # Reports Tab
    story.append(Paragraph("📊 Reports Tab", subheading_style))
    reports_features = """
    <b>Frontend Features:</b>
    • Date range selection for report generation
    • Multiple report format options
    • Data visualization charts and graphs
    • Export functionality (PDF, Excel)
    • Real-time statistics dashboard
    
    <b>Backend Integration:</b>
    • Database query optimization
    • Statistical analysis algorithms
    • Report template engine
    • Data aggregation and filtering
    • Automated scheduling system
    """
    story.append(Paragraph(reports_features, styles['Normal']))
    
    # Settings Tab
    story.append(Paragraph("⚙️ Settings Tab", subheading_style))
    settings_features = """
    <b>Frontend Features:</b>
    • System configuration panels
    • Camera calibration interface
    • Threshold adjustment controls
    • User preference settings
    • System diagnostics display
    
    <b>Backend Integration:</b>
    • Configuration file management
    • System parameter validation
    • Hardware communication protocols
    • Backup and restore functionality
    • Performance monitoring
    """
    story.append(Paragraph(settings_features, styles['Normal']))
    story.append(PageBreak())
    
    # User Management System
    story.append(Paragraph("4. User Management System", heading_style))
    
    story.append(Paragraph("4.1 User Management Tab", subheading_style))
    user_mgmt_features = """
    <b>Frontend Features:</b>
    • Two-panel layout with user list and details form
    • Real-time search and filtering capabilities
    • Role-based access control interface
    • Password change dialogs with validation
    • Bulk user operations support
    
    <b>Backend Integration:</b>
    • MySQL database with optimized queries
    • Secure password hashing and salt generation
    • User session management
    • Audit trail logging
    • Input validation and sanitization
    """
    story.append(Paragraph(user_mgmt_features, styles['Normal']))
    
    story.append(Paragraph("4.2 CRUD Operations", subheading_style))
    crud_data = [
        ['Operation', 'Frontend Interface', 'Backend Process'],
        ['Create', 'New user form with validation', 'Password hashing, database insertion'],
        ['Read', 'User list with search/filter', 'Optimized database queries'],
        ['Update', 'Editable user details form', 'Validation, secure updates'],
        ['Delete', 'Confirmation dialog', 'Cascading deletes, audit logging']
    ]
    
    crud_table = Table(crud_data, colWidths=[1*inch, 2.5*inch, 2.5*inch])
    crud_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(crud_table)
    
    # Database Schema
    story.append(Paragraph("5. Database Schema", heading_style))
    
    story.append(Paragraph("5.1 Users Table", subheading_style))
    users_schema = """
    <b>Table: users</b>
    • id (INT, PRIMARY KEY, AUTO_INCREMENT)
    • employee_id (VARCHAR, UNIQUE, NOT NULL)
    • email (VARCHAR, UNIQUE, NOT NULL)
    • password_hash (VARCHAR, NOT NULL)
    • salt (VARCHAR, NOT NULL)
    • role (ENUM: 'User', 'Admin', 'Super Admin')
    • first_name (VARCHAR)
    • last_name (VARCHAR)
    • is_active (BOOLEAN, DEFAULT TRUE)
    • failed_login_attempts (INT, DEFAULT 0)
    • last_login (TIMESTAMP)
    • created_at (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)
    • updated_at (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP ON UPDATE)
    """
    story.append(Paragraph(users_schema, styles['Normal']))
    
    # System Features
    story.append(Paragraph("6. Advanced System Features", heading_style))
    
    story.append(Paragraph("6.1 Error Handling", subheading_style))
    error_handling = """
    • Comprehensive exception handling throughout the application
    • User-friendly error messages and validation feedback
    • Automatic error logging and debugging information
    • Graceful degradation for hardware failures
    • Recovery procedures for database connection issues
    """
    story.append(Paragraph(error_handling, styles['Normal']))
    
    story.append(Paragraph("6.2 Performance Optimization", subheading_style))
    performance = """
    • Multi-threaded camera processing for smooth real-time display
    • Optimized database queries with proper indexing
    • Efficient memory management for image processing
    • Lazy loading for large datasets
    • Caching mechanisms for frequently accessed data
    """
    story.append(Paragraph(performance, styles['Normal']))
    
    story.append(Paragraph("6.3 Security Measures", subheading_style))
    security_measures = """
    • SQL injection prevention through parameterized queries
    • Input validation and sanitization
    • Secure password storage with SHA-256 and salt
    • Session timeout and automatic logout
    • Role-based access control enforcement
    • Audit logging for all critical operations
    """
    story.append(Paragraph(security_measures, styles['Normal']))
    story.append(PageBreak())
    
    # Deployment and Maintenance
    story.append(Paragraph("7. Deployment and Maintenance", heading_style))
    
    story.append(Paragraph("7.1 System Requirements", subheading_style))
    requirements = """
    <b>Software Requirements:</b>
    • Python 3.13 or higher
    • MySQL 8.0 or higher
    • OpenCV 4.x
    • Tkinter (included with Python)
    • Required Python packages (see requirements.txt)
    
    <b>Hardware Requirements:</b>
    • Minimum 8GB RAM (16GB recommended)
    • Multi-core processor (Intel i5 or equivalent)
    • USB 3.0 ports for camera connections
    • Minimum 1920x1080 display resolution
    """
    story.append(Paragraph(requirements, styles['Normal']))
    
    story.append(Paragraph("7.2 Installation Guide", subheading_style))
    installation = """
    1. Install Python 3.13 and required dependencies
    2. Set up MySQL database and create welvision_db
    3. Run database initialization scripts
    4. Configure camera connections and settings
    5. Execute main.py to launch the application
    6. Complete initial user setup and configuration
    """
    story.append(Paragraph(installation, styles['Normal']))
    
    # Future Enhancements
    story.append(Paragraph("8. Future Enhancement Opportunities", heading_style))
    
    enhancements = """
    • Web-based interface for remote access
    • Advanced AI models for defect detection
    • Integration with enterprise ERP systems
    • Mobile application for notifications
    • Advanced analytics and machine learning
    • Cloud deployment and scalability options
    • API development for third-party integrations
    """
    story.append(Paragraph(enhancements, styles['Normal']))
    
    # Conclusion
    story.append(Paragraph("9. Conclusion", heading_style))
    conclusion = """
    The WelVision application represents a comprehensive solution for industrial vision inspection 
    with robust user management capabilities. The system demonstrates enterprise-grade security, 
    scalable architecture, and user-friendly interface design. The modular structure allows for 
    easy maintenance and future enhancements while maintaining high performance and reliability.
    """
    story.append(Paragraph(conclusion, styles['Normal']))
    
    # Build PDF
    doc.build(story)
    print("✅ Documentation PDF generated successfully: WelVision_Application_Documentation.pdf")

if __name__ == "__main__":
    try:
        create_documentation()
    except ImportError as e:
        print("❌ Error: ReportLab library is required to generate PDF documentation.")
        print("Please install it using: pip install reportlab")
        print(f"Error details: {e}")
    except Exception as e:
        print(f"❌ Error generating documentation: {e}") 