# Face Recognition Attendance System

## Description
The Face Recognition Attendance System is an intelligent solution designed to automate the attendance tracking process using facial recognition. This system leverages machine learning and computer vision techniques to accurately identify individuals and record their attendance in a real-time environment.

The project integrates a camera feed, processes images to detect and recognize faces, and updates attendance records in a MySQL database. It also allows users to manage person details, generate attendance reports, and download them in CSV format.

---

## Features

- **Real-time Face Recognition**: Automatically identifies individuals using their face and marks their attendance.
- **Database Integration**: Utilizes MySQL to store and manage attendance records, person details, and images.
- **CSV Report Generation**: Generates and allows downloading of daily attendance reports in CSV format.
- **Dataset Management**: Allows capturing images of people and associating them with unique identifiers.
- **Web Interface**: Built using Flask to interact with the system and manage records.
  
---
## Project Gallery

Here are some screenshots of the application in action:

### 1. Home Page (Add Person and View Attendance)
![Home Page](https://github.com/Yashparmar1125/Face_Attendence_System/blob/master/Screenshots/home.png)

### 2. Add Person Form
![Add Person Form](https://github.com/Yashparmar1125/Face_Attendence_System/blob/master/Screenshots/AddStudent.png)

### 3. Face Recognition in Action
![Face Recognition](https://github.com/Face_Attendence_System/Screenshots/attendence.pnghttps://github.com/Yashparmar1125/Face_Attendence_System/blob/master/Screenshots/attendence.png
### 4. Students Logs 
![Attendance Logs](https://github.com/Yashparmar1125/Face_Attendence_System/blob/master/Screenshots/Students.png)

---
## Installation

### Prerequisites
1. **Python**: Ensure that Python 3.x is installed on your system.
2. **MySQL**: A running MySQL server instance with a database named `attendence_record`.

### Install Dependencies
1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/face-recognition-attendance.git
   cd face-recognition-attendance
   
2. Install required libraries:
   ```bash
   pip install requirements.txt
   
3. Set up the MySQL database by executing the following SQL script:
    ```sql
   CREATE DATABASE attendence_record;

    USE attendence_record;
    
    -- Create person_details table
    CREATE TABLE person_details (
        prs_nbr INT PRIMARY KEY,
        prs_name VARCHAR(255),
        prs_skill VARCHAR(255),
        prs_active BOOLEAN DEFAULT TRUE,
        prs_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Create img_dataset table
    CREATE TABLE img_dataset (
        img_id INT PRIMARY KEY,
        img_person INT,
        FOREIGN KEY (img_person) REFERENCES person_details(prs_nbr)
    );
    
    -- Create attendence_history table
    CREATE TABLE attendence_history (
        accs_id INT AUTO_INCREMENT PRIMARY KEY,
        accs_prsn INT,
        accs_date DATE,
        accs_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (accs_prsn) REFERENCES person_details(prs_nbr)
    );
---
## Usage
1.  Running the Application: To start the application, run the following command:
    ```bash
        python app.py

2. Accessing the Web Interface: Open your web browser and go to http://localhost:5000.

---
## Configuration
The following configuration parameters are required to connect the system to your MySQL database:

    Host: localhost
    User: root
    Password: your_mysql_password
    Database: attendence_record
These parameters can be set in the app.py file or using environment variables.

---
## Contributing
We welcome contributions to enhance the SCMS! Follow these steps to contribute:

1. Fork the repository.
2. Create a new feature branch:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add new feature"
   ```
4. Push the branch:
   ```bash
   git push origin feature-name
   ```
5. Open a Pull Request.

---
## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Contact
For any queries or support, feel free to reach out:
- **Author**: Yash Parmar
- **GitHub**: [https://github.com/Yashparmar1125](https://github.com/Yashparmar1125)
- **Email**: [yashparmar11y@gmail.com](mailto:yashparmar11y@gmail.com)
