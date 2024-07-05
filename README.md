This repository contains my semester-end project in the subject Advanced Programming Concepts. It is a web application using flask in Python that is intended to enable the management of medication stocks in hospitals or doctor's offices.
It features user authentication, medication management, patient records, and statistical analysis. Users can register through the /register route using their name, email, password, and a hospital key, and log in via the /login route with their email and password. Logging out is handled by the /logout route, which deletes the authentication token.

The home route (/) displays a list of all medications, including details such as dosage, stock, and manufacturer. Authorized users can add new medications through the /add route, update medication stock via the /update route when amounts are taken, and restock medications through the /restock route.

The /patients route provides an overview of all patients, showing their room number and name. Detailed records of a specific patient, including their diagnosis and needed medications, can be viewed through the /patient/<patient_id> route. Additionally, the /update_patient_medications/<patient_id> route updates the medication stock based on the patient's medication needs.

For statistical analysis, the /statistics route displays medication stock statistics and an activity log of user actions, while the /plot.png route generates a bar chart visualization of medication stock levels.
