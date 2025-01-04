import os
import requests
import flickr_api
from datetime import datetime
from flickr_api import auth
from PIL import Image, ExifTags
from piexif import ExifIFD, dump, insert
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the environment variables
FLICKR_API_KEY = os.getenv("FLICKR_API_KEY")
FLICKR_API_SECRET = os.getenv("FLICKR_API_SECRET")

flickr_api.set_keys(api_key=FLICKR_API_KEY, api_secret=FLICKR_API_SECRET)

# Authenticate user
def authenticate():
    try:
        # Initialize authentication handler
        a = auth.AuthHandler()
        print("Visit this URL to authenticate:", a.get_authorization_url("delete"))
        verifier = input("Enter the verifier code you received: ")
        a.set_verifier(verifier)
        
        # Save credentials to a file
        a.save("flickr_auth.txt")
        print("Authentication credentials saved to 'flickr_auth.txt'")
        flickr_api.set_auth_handler(a)
    except Exception as e:
        print(f"Error during authentication: {e}")
        raise


# Load authentication if available
if os.path.exists("flickr_auth.txt"):
    flickr_api.set_auth_handler("flickr_auth.txt")
else:
    authenticate()

def log_message(log_file, message):
    with open(log_file, "a", encoding="utf-8") as log:
        log.write(message + "\n")

def sanitize_title(title):
    # Replace problematic characters in the title
    invalid_chars = ["/", "\\", "?", "*", "\"", "<", ">", "|", ":"]
    for char in invalid_chars:
        title = title.replace(char, "-")
    return title.strip()

def add_exif_to_image(file_path, metadata):
    try:
        # Convert Unix timestamp to EXIF-compatible format
        dateuploaded = metadata.get("dateuploaded", None)
        if dateuploaded:
            try:
                formatted_dateuploaded = datetime.utcfromtimestamp(int(dateuploaded)).strftime("%Y:%m:%d %H:%M:%S")
            except ValueError:
                formatted_dateuploaded = "0000:00:00 00:00:00"
        else:
            formatted_dateuploaded = "0000:00:00 00:00:00"

        # Prepare EXIF data
        exif_dict = {
            "0th": {
                271: metadata.get("camera", "Unknown Camera"),  # Exif tag for Make
                272: metadata.get("model", "Unknown Model"),  # Exif tag for Model
                306: formatted_dateuploaded,  # Exif tag for DateTime
                270: metadata.get("title", "No Title")  # Exif tag for ImageDescription
            },
            "Exif": {
                36867: metadata.get("datetaken", "0000:00:00 00:00:00"),  # Exif tag for DateTimeOriginal
                36868: formatted_dateuploaded  # Exif tag for DateTimeDigitized
            }
        }

        exif_bytes = dump(exif_dict)

        # Insert EXIF data into the image
        insert(exif_bytes, file_path)
        print(f"EXIF data added to: {file_path}")
    except Exception as e:
        print(f"Failed to add EXIF data to {file_path}: {e}")

def photo_already_downloaded(photo_id, album_directory):
    # Check if a photo with the given ID already exists in the directory
    file_path = os.path.join(album_directory, f"{photo_id}.jpg")
    return os.path.exists(file_path)

def delete_photo(photo_id):
    try:
        photo = flickr_api.Photo(id=photo_id)
        photo.delete()
        print(f"Photo {photo_id} deleted successfully from Flickr.")
    except Exception as e:
        print(f"Failed to delete photo {photo_id}: {e}")


def download_album_photos(album_id, album_name, base_directory, log_file):
    try:
        # Fetch album info
        album = flickr_api.Photoset(id=album_id)
        photos = album.getPhotos()

        # Create a folder for the album
        album_directory = os.path.join(base_directory, album_name)
        if not os.path.exists(album_directory):
            os.makedirs(album_directory)

        downloaded_count = 0

        # Download photos and metadata
        for photo in photos:
            photo_info = photo.getInfo()
            photo_id = photo_info.get("id")

            # Skip downloading if photo already exists
            if photo_already_downloaded(photo_id, album_directory):
                print(f"Skipping already downloaded photo: {photo_id}")
                continue

            title = sanitize_title(photo_id)
            sizes = photo.getSizes()
            url = sizes.get("Original", sizes.get("Large", {})).get("source", None)

            if url:
                file_path = os.path.join(album_directory, f"{title}.jpg")

                print(f"Downloading: {title}")

                # Download photo
                response = requests.get(url, stream=True)
                if response.status_code == 200:
                    with open(file_path, "wb") as file:
                        for chunk in response.iter_content(1024):
                            file.write(chunk)

                    # Add EXIF data to the photo
                    add_exif_to_image(file_path, photo_info)
                    downloaded_count += 1

                    # Delete photo from Flickr
                    delete_photo(photo_id)
                else:
                    error_message = f"Failed to download photo: {title}, URL: {url}"
                    print(error_message)
                    log_message(log_file, error_message)

            else:
                error_message = f"No URL found for photo: {title}"
                print(error_message)
                log_message(log_file, error_message)

        print(f"All photos and metadata for album '{album_name}' downloaded to {album_directory}")
        print(f"Total photos downloaded for album '{album_name}': {downloaded_count}")
    except Exception as e:
        error_message = f"Error processing album {album_name} (ID: {album_id}): {e}"
        print(error_message)
        log_message(log_file, error_message)

if __name__ == "__main__":
    # List of albums to download (name and ID pairs)
    albums = [
        {"name": "Beijing Pics", "id": "72157715429434398"}
    ]

    # Base directory to save albums
    BASE_DIRECTORY = "./flickr_albums"

    # Log file to record errors and statuses
    LOG_FILE = "flickr_download.log"

    for album in albums:
        download_album_photos(album["id"], album["name"], BASE_DIRECTORY, LOG_FILE)