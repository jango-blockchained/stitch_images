from PIL import Image
import os
import psutil

def calculate_batch_size(image_folder, percent_of_memory, max_images):
    """
    Calculate the batch size based on available memory.

    Args:
        image_folder (str): Path to the source image folder.
        percent_of_memory (float): Percentage of available memory to be used.
        max_images (int): Maximum number of images to be used.

    Returns:
        int: Calculated batch size based on available memory.

    """
    first_image_path = os.path.join(image_folder, os.listdir(image_folder)[0])
    first_image = Image.open(first_image_path)
    size_of_image = first_image.size[0] * first_image.size[1] * 3  # width * height * 3 bytes (for RGB)

    memory_info = psutil.virtual_memory()
    available_memory = memory_info.available  # in bytes

    images_in_memory = (available_memory * percent_of_memory) // size_of_image
    images_to_use = min(images_in_memory, max_images)

    return int(images_to_use)

def get_estimated_image_size(image_folder, max_images):
    """
    Get the estimated image size in pixels and kilobytes.

    Args:
        image_folder (str): Path to the source image folder.
        max_images (int): Maximum number of images to be used.

    Returns:
        tuple: Tuple containing image width, height, and total size in kilobytes.

    """
    images = sorted([img for img in os.listdir(image_folder) if img.endswith((".jpg", ".png", ".tiff"))])

    first_image_path = os.path.join(image_folder, images[0])
    first_image = Image.open(first_image_path)

    image_width = first_image.width
    image_height = first_image.height
    total_image_size = (image_width * image_height * 3 * max_images) // 1024  # in kilobytes

    return image_width, image_height, total_image_size

def stitch_images(image_folder, output_file, batch_size):
    """
    Stitch the images from the source folder and save as a single image.

    Args:
        image_folder (str): Path to the source image folder.
        output_file (str): Path to the output file (including filename).
        batch_size (int): Number of images to be processed at a time.

    """
    images = sorted([img for img in os.listdir(image_folder) if img.endswith((".jpg", ".png", ".tiff"))])

    first_img = Image.open(os.path.join(image_folder, images[0]))
    total_height = len(images) * first_img.height
    new_img = Image.new('RGB', (first_img.width, total_height))

    y_offset = 0
    for i in range(0, len(images), batch_size):
        for img_name in images[i:i+batch_size]:
            img = Image.open(os.path.join(image_folder, img_name))
            new_img.paste(img, (0, y_offset))
            y_offset += img.height
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)  # Create the output folder if it doesn't exist
        new_img.save(output_file)

# Get user input for source image folder
default_image_folder = "data/src/"
image_folder = input(f"Please enter the path to the source image folder (default: {default_image_folder}): ") or default_image_folder

# Use default destination folder if not provided by user
default_dest_folder = "data/output/"
dest_folder = input(f"Please enter the path to the destination folder (default: {default_dest_folder}): ") or default_dest_folder

# Use default output file if not provided by user
default_output_file = "stitched_image.tif"
output_file = input(f"Please enter the output filename: {default_output_file}): ") or default_output_file

# Prompt the user to choose batch size option
choice = input("Enter 'A' for automatic batch size calculation or 'M' for manual input: ")

if choice.upper() == "A":
    # Calculate the batch size based on the available memory
    max_images = int(input("Enter the maximum number of images to use: "))

    image_width, image_height, total_image_size = get_estimated_image_size(image_folder, max_images)
    print(f"\nEstimated Image Size:")
    print(f"Width: {image_width}px, Height: {image_height}px")
    print(f"Total Size: {total_image_size}KB")

    confirm = input("\nDo you want to continue? (Y/N): ")
    if confirm.upper() != "Y":
        print("Process aborted.")
        exit()

    batch_size = calculate_batch_size(image_folder, 0.5, max_images)  # use 50% of available memory
    print(f"Batch size calculated: {batch_size}")

elif choice.upper() == "M":
    batch_size = int(input("Enter the batch size: "))
else:
    print("Invalid choice. Using automatic batch size calculation.")

    max_images = int(input("Enter the maximum number of images to use: "))

    image_width, image_height, total_image_size = get_estimated_image_size(image_folder, max_images)
    print(f"\nEstimated Image Size:")
    print(f"Width: {image_width}px, Height: {image_height}px")
    print(f"Total Size: {total_image_size}KB")

    confirm = input("\nDo you want to continue? (Y/N): ")
    if confirm.upper() != "Y":
        print("Process aborted.")
        exit()

    batch_size = calculate_batch_size(image_folder, 0.5, max_images)  # use 50% of available memory
    print(f"Batch size calculated: {batch_size}")

# Pass the batch size to the stitching function
stitch_images(image_folder, os.path.join(dest_folder, output_file), batch_size)
