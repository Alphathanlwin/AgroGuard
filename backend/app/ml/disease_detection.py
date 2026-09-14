import os
import json
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image

# Global variables to hold the loaded model and classes
_model = None
_class_names = None
_device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

def load_model():
    global _model, _class_names
    
    base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'artifacts')
    model_path = os.path.join(base_dir, 'disease_model.pth')
    classes_path = os.path.join(base_dir, 'disease_classes.json')
    
    if not os.path.exists(model_path) or not os.path.exists(classes_path):
        return False
        
    with open(classes_path, 'r') as f:
        _class_names = json.load(f)
        
    # Initialize ResNet18
    _model = models.resnet18(weights=None)
    num_ftrs = _model.fc.in_features
    _model.fc = nn.Linear(num_ftrs, len(_class_names))
    
    # Load weights
    _model.load_state_dict(torch.load(model_path, map_location=_device))
    _model = _model.to(_device)
    _model.eval()
    
    return True

def predict_image(image_bytes):
    """
    Predicts the disease from an image byte stream.
    Returns: dict with plant name, disease name, health status, and confidence.
    """
    global _model, _class_names
    
    if _model is None:
        success = load_model()
        if not success:
            raise Exception("Model files not found. Please train the model first.")

    # Image transformation pipeline (same as validation)
    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    # Open image from bytes
    import io
    image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    
    # Preprocess
    input_tensor = transform(image)
    input_batch = input_tensor.unsqueeze(0).to(_device)
    
    # Inference
    with torch.no_grad():
        output = _model(input_batch)
        probabilities = torch.nn.functional.softmax(output[0], dim=0)
        
    # Get top prediction
    confidence, predicted_idx = torch.max(probabilities, 0)
    class_id = _class_names[predicted_idx.item()]
    
    # Parse the class name (Format: "Plant___Disease_name")
    parts = class_id.split('___')
    plant_name = parts[0].replace('_', ' ')
    disease_name = parts[1].replace('_', ' ') if len(parts) > 1 else "Unknown"
    
    is_healthy = 'healthy' in disease_name.lower()
    
    return {
        "raw_class": class_id,
        "plant": plant_name,
        "disease": "Healthy" if is_healthy else disease_name,
        "is_healthy": is_healthy,
        "confidence": round(confidence.item() * 100, 2)
    }
