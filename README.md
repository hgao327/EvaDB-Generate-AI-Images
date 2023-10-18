# EvaDB-Generate-AI-Images
This is a project using EvaDB and LocalAI to generate the AI based Images

## - 💻 Environment Set:

### To use LocalAI, set the docker environment:

https://localai.io/howtos/easy-setup-docker-cpu/
### Load the model from LocalAI:

https://localai.io/features/image-generation/

For Example
```bash
curl http://localhost:8080/models/apply -H "Content-Type: application/json" -d '{
  "url": "github:go-skynet/model-gallery/stablediffusion.yaml"
}'
```

## - 📖 Implementation details

The Project presents an interface with EvaDB (a hypothetical database system), through which users can generate and view images based on their input commands. Here are the implementation details:

#### 1. **Initialization**

- The `EvaDBManager` class serves as the main interface with EvaDB.
- Upon instantiation of an `EvaDBManager` object, it connects to EvaDB and initializes a cursor to execute SQL queries.

```python
class EvaDBManager:
    def __init__(self):
        self.conn = evadb.connect()
        self.cursor = self.conn.cursor()

    def query(self, sql):
        return self.cursor.query(sql).df()
```

#### 2. **Function Management**

- `create_function`: Creates a function named `GenerateImage` in the database, with its implementation coming from 'test.py'.

```python
    def create_function(self):
        self.query("""
            CREATE FUNCTION
            IF NOT EXISTS GenerateImage
            IMPL 'test.py';
        """)
```

- `list_all_functions`: Returns a list of all functions present in the database.

```python
    def list_all_functions(self):
        return self.query("SHOW FUNCTIONS;")
```

- `cleanup`: Removes the previously created `GenerateImage` function.

```python
def cleanup(self):
    self.query("DROP FUNCTION GenerateImage")
```

#### 3. **Database Setup**

- `setup_database`:

  - Drops (if it exists) a table named `History`.

  - Creates a new table `History` with fields id, command, and data.

  ```python
      def setup_database(self):
          self.query("DROP TABLE IF EXISTS History")
          self.query("""
              CREATE TABLE History
              (id INTEGER,
              command TEXT(30),
              data TEXT(30));
          """)
  ```

#### 4. **Command History**

- `insert_command_to_history`: Inserts the user-inputted command into the `History` table.

```python
    def insert_command_to_history(self, id, command):
        self.query(f"""
            INSERT INTO History (id, command, data ) VALUES
            ('{id}', '{command}', 'null');
        """)
```

- `get_generated_image_url`: Retrieves the image URL associated with a specific ID from the `History` table.

```python
    def get_generated_image_url(self, id):
        query = self.query(f"""
            SELECT GenerateImage(command).result FROM History
            WHERE id = {id};
        """)
        return query['generateimage.result'].iloc[0]
```

#### 5. **Image Display**

- There are two functions to fetch and display images from a URL: `display_image_from_url_pop` and `display_image_from_url`. Their working principle is basically the same, fetching the image by sending an HTTP request, and then displaying it. The difference lies in how they display the image (using different methods).

```python
def display_image_from_url(url):
    response = requests.get(url)
    if response.status_code == 200: 
        image_data = BytesIO(response.content)
        img = Image(data=image_data.getvalue())
        display(img)
    else:
        print(f"Failed to retrieve the image. HTTP Status Code: {response.status_code}")
```

#### 6. **Main Execution Logic**

- Initializes the database connection.
- Displays all functions in the database.
- Creates the function for generating images in the database.
- Sets up the database table.
- Uses a loop to continuously prompt the user for input.
  - If the user inputs "exit", the loop is exited.
  - Otherwise, inserts the user's input command into the `History` table.
  - Retrieves the URL of the generated image.
  - Displays the image using the URL.
  - Increments the ID, preparing for the next command.
- Finally, cleanup: Removes the created function.

#### 7. Backend Model details

- **EvaDB Registration**

```python
class GenerateImage(AbstractFunction):
    @setup(cacheable=False, function_type="GenerateImage", batchable=False)
    def setup(self):
        pass

    @property
    def name(self) -> str:
        return "GenerateImage"

    @forward(
        input_signatures=[
            PandasDataframe(
                columns=["command"],
                column_types=[NdArrayType.STR],
                column_shapes=[(None,)],
            )
        ],
        output_signatures=[
            PandasDataframe(
                columns=["result"],
                column_types=[NdArrayType.STR],
                column_shapes=[(None,)],
            )
        ],
    )
    def forward(self, df: pd.DataFrame) -> pd.DataFrame:
        input_data = df.iloc[0, 0]
        url = "http://localhost:8080/v1/images/generations"
        headers = {
            "Content-Type": "application/json",
        }
        data = {
            "prompt": input_data,
            "size": "256x256",
        }

        response = requests.post(url, headers=headers, json=data)
        response_data = json.loads(response.text)
        # print(response_data)
        # Extract the URL from the parsed response
        url_extracted = response_data["data"][0]["url"]
        df = pd.DataFrame({'result': [url_extracted]})
        # print(df)
        return df
```

- **Platform and Technology Selection**:
  - Utilize LocalAI as the core platform, which supports various image generation techniques.
  - Implement the Stable Diffusion method using a backend written in C++, an advanced technique in the field of image generation.

- **Model Configuration & Setup**:
  - Use a pre-defined model configuration file to specify the parameters and backend needed for image generation.
  - The model is automatically downloaded from huggingface upon its first use.

- **Image Generation Process**:
  - Users send a POST request to a specific endpoint with the prompt (e.g., "A cute baby sea otter") required for generating the image.
  - LocalAI processes this request and generates the image using the Stable Diffusion technique and the specified backend.
  - The generated image is returned to the user in the form of a URL.

- **Extended Features**:
  - For intricate or specific image requirements, users can provide a more detailed prompt and separate positive and negative hints using "|".
  - If necessary, users can also upscale the generated image or perform other modifications using external tools.

This implementation leverages the LocalAI platform and the Stable Diffusion technique to produce and provide images upon receiving descriptive requests from users.
