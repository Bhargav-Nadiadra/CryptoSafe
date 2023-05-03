import os
import base64
from cryptography.fernet import Fernet
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import smtplib
from email.mime.text import MIMEText
import streamlit as st

def encrypt_file(file_buffer):
    # Define your Azure Blob Storage connection string and container name
    connection_string = "DefaultEndpointsProtocol=https;AccountName=cloudlabdone;AccountKey=5nwjwRWSXHmX4fp6q+20KTT83t4t+dre0RR8kFYbOf5SqgPC7/AhF61xSR6CG6OMroowyK3oPyTz+AStkp7urA==;EndpointSuffix=core.windows.net"
    container_name = "demo"

    # Generate a Fernet key
    key = Fernet.generate_key()

    # Initialize the Fernet cipher with the key
    cipher = Fernet(key)

    # Read the contents of the plaintext file
    plaintext = file_buffer.read()

    # Encrypt the plaintext using the Fernet cipher
    encrypted_plaintext = cipher.encrypt(plaintext)

    # Initialize the BlobServiceClient with your connection string
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Create the container if it doesn't already exist
    container_client = blob_service_client.get_container_client(container_name)
    if not container_client.exists():
        container_client.create_container()

    # Upload the encrypted file to the container
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_buffer.name)
    blob_client.upload_blob(encrypted_plaintext)

    # Send the key to your Mailtrap account
    mailtrap_username = "5fc6e4f0852836"
    mailtrap_password = "9f2bcf66ae6ff4"
    recipient_email = "bhargavnadiadra@outlook.com"

    message = MIMEText(key.decode())
    message['Subject'] = 'Fernet key for encrypted file'
    message['From'] = 'bhargavnadiadra@outlook.com'
    message['To'] = recipient_email

    smtp_server = smtplib.SMTP('smtp.mailtrap.io', 2525)
    smtp_server.login(mailtrap_username, mailtrap_password)
    smtp_server.sendmail('bhargavnadiadra@outlook.com', recipient_email, message.as_string())
    smtp_server.quit()

    return key.decode()

def decrypt_file(file_buffer, key):
    connection_string = "DefaultEndpointsProtocol=https;AccountName=cloudlabdone;AccountKey=5nwjwRWSXHmX4fp6q+20KTT83t4t+dre0RR8kFYbOf5SqgPC7/AhF61xSR6CG6OMroowyK3oPyTz+AStkp7urA==;EndpointSuffix=core.windows.net"
    container_name = "demo"

    # Create BlobServiceClient object
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Download encrypted file from Azure Blob Storage
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_buffer.name)
    stream = blob_client.download_blob().content_as_bytes()

    # Create Fernet object for encryption/decryption with the new key
    fernet = Fernet(key.encode())

    # Decrypt data
    decrypted_data = fernet.decrypt(stream)

    return decrypted_data

# Streamlit app
st.title("File Encryption and Decryption")

option = st.sidebar.selectbox("Choose an action", ("Encrypt", "Decrypt"))

if option == "Encrypt":
    st.header("Encrypt a file")

    uploaded_file = st.file_uploader("Choose a file to encrypt", type=["txt", "docx", "pdf"])

    if uploaded_file is not None:
        key = encrypt_file(uploaded_file)
        st.success(f"File successfully encrypted and uploaded. Fernet key: {key}")

elif option == "Decrypt":
    st.header("Decrypt a file")

    uploaded_file = st.file_uploader("Choose a file to decrypt", type=["txt", "docx", "pdf"])

    if uploaded_file is not None:
        key = st.text_input("Enter the Fernet key:")
        if st.button("Decrypt"):
            try:
                decrypted_data = decrypt_file(uploaded_file, key)
                st.success("File successfully decrypted.")
                
                # Convert the decrypted data into a downloadable file
                b64 = base64.b64encode(decrypted_data).decode()
                href = f'<a href="data:file/txt;base64,{b64}" download="decrypted_{uploaded_file.name}">Download decrypted file</a>'
                st.markdown(href, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Error: {e}")
                st.write("Make sure you have entered the correct Fernet key and uploaded the correct encrypted file.")
                



#Accountname: cloudlabdone
# container name: demo 
# blob name: test.txt
# accesskey : key 1 ni at key connection key 
#streamlit run test.py
