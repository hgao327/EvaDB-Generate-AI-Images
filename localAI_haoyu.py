import time
from io import BytesIO
import requests
from IPython.core.display_functions import display
from PIL import Image
import evadb


class EvaDBManager:
    def __init__(self):
        self.conn = evadb.connect()
        self.cursor = self.conn.cursor()

    def query(self, sql):
        return self.cursor.query(sql).df()

    def create_function(self):
        self.query("""
            CREATE FUNCTION
            IF NOT EXISTS GenerateImage
            IMPL 'test.py';
        """)

    def setup_database(self):
        self.query("DROP TABLE IF EXISTS History")
        self.query("""
            CREATE TABLE History
            (id INTEGER,
            command TEXT(30),
            data TEXT(30));
        """)

    def insert_command_to_history(self, id, command):
        self.query(f"""
            INSERT INTO History (id, command, data ) VALUES
            ('{id}', '{command}', 'null');
        """)

    def get_generated_image_url(self, id):
        query = self.query(f"""
            SELECT GenerateImage(command).result FROM History
            WHERE id = {id};
        """)
        return query['generateimage.result'].iloc[0]

    def list_all_functions(self):
        return self.query("SHOW FUNCTIONS;")

    def cleanup(self):
        self.query("DROP FUNCTION GenerateImage")


def display_image_from_url_pop(url):
    response = requests.get(url)
    if response.status_code == 200:
        image_data = BytesIO(response.content)
        image = Image.open(image_data)
        image.show()
    else:
        print(f"Failed to retrieve the image. HTTP Status Code: {response.status_code}")


def display_image_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        image_data = BytesIO(response.content)
        img = Image(data=image_data.getvalue())
        display(img)
    else:
        print(f"Failed to retrieve the image. HTTP Status Code: {response.status_code}")


if __name__ == "__main__":
    # Connect to EvaDB
    db_manager = EvaDBManager()

    # Show functions
    print(db_manager.list_all_functions())

    print("Welcome to Evadb based AI Image Generation Program !!")

    # Create function for generating images
    db_manager.create_function()
    print("Function Ready")

    # Setup the database
    db_manager.setup_database()

    id = 1
    while True:
        start_time = time.time()
        # Get user input from the command line
        user_input = input("Please enter the image you want (or type 'exit' to quit): ")

        # Check if the user wants to exit
        if user_input.lower() == 'exit':
            break

        # Insert command to history
        db_manager.insert_command_to_history(id, user_input)

        # Generate image
        url_image = db_manager.get_generated_image_url(id)

        # Display the image
        display_image_from_url_pop(url_image)

        id += 1
        end_time = time.time()
        print("程序运行时间：", end_time - start_time, "秒")

    # Cleanup
    db_manager.cleanup()

