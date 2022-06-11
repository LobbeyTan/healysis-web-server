from app import app
from src.populate import populateData

if __name__ == "__main__":
    # populateData()
    app.run(host='0.0.0.0', port=5000)
    # app.run(host='127.0.0.1', port=5000, debug=True)
