from app import app
from src.populate import populateData

if __name__ == "__main__":
    # populateData()
    app.run(host='0.0.0.0', port=5000)
