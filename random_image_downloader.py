import os
import requests

def download_image(url, filename):
    response = requests.get(url, stream=True)

    # Check if the request was successful
    if response.status_code == 200:
        # Open the output file in binary mode
        with open(filename, 'wb') as out_file:
            # Copy the response content (which is in binary format) to the file
            out_file.write(response.content)

# Set the URL for the API endpoint
base_url = "https://picsum.photos/800/600"

# Set the directory to save the images
directory = "./data/src"

# Download 200 images
for i in range(200):
    # Create a filename for each image
    filename = os.path.join(directory, f"image_{i+1}.tiff")

    # Download the image
    download_image(base_url, filename)

print("Finished downloading images.")
