from fastapi import FastAPI, HTTPException, UploadFile, File 
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import io

# Import from your actual files
from .models import PrescriptionRequest, VerificationResponse, Drug
from .nlp_utils import extract_drugs_from_text
from .drug_utils import check_interactions, check_dosage, get_alternatives
from .ocr_processor import ocr_processor  # ← CHANGED TO OCR PROCESSOR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="MedSafe AI API", version="1.0.0")

# Configure CORS to allow requests from the Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],  # Streamlit's default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/verify")
async def verify_prescription(request: PrescriptionRequest):
    """Main endpoint to verify a prescription."""
    try:
        drugs_to_check = request.drugs

        # 1. Extract drugs from text if provided
        if request.text_input:
            extracted_drugs = extract_drugs_from_text(request.text_input)
            logger.info(f"Extracted drugs from text: {extracted_drugs}")
            # Convert extracted drugs to Drug objects if needed
            for drug_info in extracted_drugs:
                drugs_to_check.append(Drug(
                    name=drug_info.get('name', ''),
                    dosage=drug_info.get('dosage', ''),
                    frequency=drug_info.get('frequency', '')
                ))

        if not drugs_to_check:
            return VerificationResponse(
                is_safe=True,
                extracted_drugs=[],
                interactions=[],
                dosage_alerts=[],
                alternatives=[]
            )

        # 2. Check for drug interactions
        interaction_alerts = check_interactions(drugs_to_check, request.patient.age)

        # 3. Check dosage for each drug
        dosage_alerts = []
        for drug in drugs_to_check:
            dosage_alerts.extend(check_dosage(drug, request.patient.age))

        # 4. Suggest alternatives for problematic drugs
        alternative_suggestions = []
        for alert in interaction_alerts + dosage_alerts:
            # Find the target drug
            target_drug_name = alert.drug_a if hasattr(alert, 'drug_a') else alert.drug
            target_drug = next(
                (d for d in drugs_to_check if d.name.lower() == target_drug_name.lower()),
                None
            )
            if target_drug:
                # Use the appropriate attribute based on alert type
                if hasattr(alert, 'description'):  # InteractionAlert
                    reason = alert.description
                else:  # DosageAlert
                    reason = alert.issue

                alts = get_alternatives(target_drug, request.patient, reason)
                alternative_suggestions.extend(alts)

        # 5. Determine overall safety
        is_safe = not (interaction_alerts or dosage_alerts)

        return VerificationResponse(
            is_safe=is_safe,
            extracted_drugs=drugs_to_check,
            interactions=interaction_alerts,
            dosage_alerts=dosage_alerts,
            alternatives=alternative_suggestions
        )

    except Exception as e:
        logger.error(f"An error occurred during verification: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/extract-text")  # ← CHANGED ENDPOINT NAME
async def extract_text_from_image(image_file: UploadFile = File(...)):
    """
    Endpoint to extract text from prescription image using OCR
    """
    try:
        # Read image file directly - no temp file needed
        image_data = await image_file.read()
        
        # Extract text using OCR
        extracted_text = ocr_processor.extract_text_from_image(image_data)
        
        return JSONResponse(content={
            "extracted_text": extracted_text,
            "success": True
        })
        
    except Exception as e:
        logger.error(f"OCR extraction error: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@app.get("/")
async def root():
    return {"message": "MedSafe AI API is running."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
