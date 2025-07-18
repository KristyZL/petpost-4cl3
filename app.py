from flask import Flask, render_template, request, redirect
import boto3, json, os, uuid

app = Flask(__name__)

# ✅ YOUR ACTUAL BUCKET NAME AND REGION
BUCKET = 'petpost-images-kristyliu'
REGION = 'us-east-1'

# ✅ Connect to S3
s3 = boto3.client('s3', region_name=REGION)

# ✅ File to store pet data (no database)
DATA_FILE = 'pets.json'
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump([], f)

@app.route('/')
def index():
    with open(DATA_FILE) as f:
        pets = json.load(f)
    return render_template('index.html', pets=pets)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        breed = request.form['breed']
        image = request.files['image']

        if image:
            # ✅ Give each image a unique name
            image_name = f"{uuid.uuid4()}_{image.filename}"

            # ✅ Upload to S3 with public-read access
            s3.upload_fileobj(
                image,
                BUCKET,
                image_name,
                ExtraArgs={"ACL": "public-read"}
            )

            # ✅ Get full S3 image URL
            image_url = f"https://{BUCKET}.s3.{REGION}.amazonaws.com/{image_name}"

            # ✅ Save pet info to pets.json
            with open(DATA_FILE, 'r+') as f:
                pets = json.load(f)
                pets.append({
                    'name': name,
                    'age': age,
                    'breed': breed,
                    'image_url': image_url
                })
                f.seek(0)
                json.dump(pets, f)

        return redirect('/')
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
