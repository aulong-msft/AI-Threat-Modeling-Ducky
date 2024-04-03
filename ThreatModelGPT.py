import os
import dotenv
import time
import requests
from io import BytesIO
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

from array import array
import os
from PIL import Image
import sys
import time

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
openai_api_endpoint = os.getenv("OPENAI_API_ENDPOINT")
computer_vision_api_key = os.getenv("COMPUTER_VISION_API_KEY")
computer_vision_api_endpoint = os.getenv("COMPUTER_VISION_API_ENDPOINT")
image_file_path = os.getenv("IMAGE_FILEPATH")
github_username = os.getenv("GITHUB_USERNAME")
github_personal_access_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")

#print the values
print(openai_api_key)
print(openai_api_endpoint)
print(computer_vision_api_key)
print(computer_vision_api_endpoint)
print(image_file_path)
print(github_username)
print(github_personal_access_token)

def read_local_image(image_path):
    endpoint = f"{computer_vision_api_endpoint}/vision/v3.2/read/analyze"
    headers = {"Ocp-Apim-Subscription-Key": computer_vision_api_key, "Content-Type": "application/octet-stream"}
    with open(image_path, "rb") as image_file:
        response = requests.post(endpoint, headers=headers, data=image_file)
        try:
            operation_url = response.headers["Operation-Location"]
            print("SUccess!!" + operation_url)
        except KeyError:
            raise Exception(response.json())


    while True:
        status_response = requests.get(operation_url, headers={"Ocp-Apim-Subscription-Key": computer_vision_api_key})
        status_response.raise_for_status()  # Raise an exception for bad status codes
        response_json = status_response.json()
        if "status" in response_json:
            status = response_json["status"]
            if status == "Succeeded":
                print("Suuuuuuucessssssssssssssss")
                break
            elif status == "Failed":
                raise Exception("Image processing failed")
        else:
            raise Exception("Status key not found in response")
        time.sleep(1)

    result_url = f"{operation_url}/analyzeResults"
    result_response = requests.get(result_url, headers={"Ocp-Apim-Subscription-Key": computer_vision_api_key})
    result = result_response.json()
    extracted_text = "\n".join([line["text"] for line in result["analyzeResult"]["readResults"][0]["lines"]])
    print("TEXT" + extracted_text)
    return extracted_text

def generate_list_of_services(text):
    prompt = f"Prompt 1: You are an Amazon AWS security engineer doing threat model analysis to identify and mitigate risk. Given the following text:\n{text}\n please find the relevant AWS Services and print them out. \n"
    response = requests.post(
        openai_api_endpoint,
        headers={"Authorization": f"Bearer {openai_api_key}"},
        json={"prompt": prompt, "max_tokens": 500, "temperature": 0.2}
    )
    return response.json()["choices"][0]["text"]

def generate_list_of_security_recommendations(text):
    prompt = f"Prompt 2:\nAs a Amazon AWS security engineer specializing in threat model analysis and risk mitigation, you have been tasked with evaluating the security posture of various AWS services:\n{text}\nYour objective is to identify service-specific security recommendations by leveraging AWS Security Basline documentation and AWS to find tailored security advice for each service.\n"
    response = requests.post(
        openai_api_endpoint,
        headers={"Authorization": f"Bearer {openai_api_key}"},
        json={"prompt": prompt, "max_tokens": 2000, "temperature": 0.5, "nucleus_sampling_factor": 0.5}
    )
    return response.json()["choices"][0]["text"]

def generate_list_of_security_threats(text):
    prompt = f"Prompt 2:\nAs a Amazon AWS security engineer specializing in threat model analysis and risk mitigation, you have been tasked with evaluating the security posture of various Amazon AWS services:\n{text}\nYour objective is to identify service-specific security threats by leveraging Microsoft STRIDE threat modeling framework documentation and Microsoft docs to find tailored security advice for each service.\n"
    response = requests.post(
        openai_api_endpoint,
        headers={"Authorization": f"Bearer {openai_api_key}"},
        json={"prompt": prompt, "max_tokens": 2000, "temperature": 0.5, "nucleus_sampling_factor": 0.5}
    )
    return response.json()["choices"][0]["text"]

def main():
    extracted_text = read_local_image(image_file_path)
    print("Extracted Text from Image:")
    print(extracted_text)

    services = generate_list_of_services(extracted_text)
    print("Services:")
    print(services)

    recommendations = generate_list_of_security_recommendations(extracted_text)
    print("Security Recommendations:")
    print(recommendations)

    threats = generate_list_of_security_threats(extracted_text)
    print("Security Threats:")
    print(threats)

if __name__ == "__main__":
    main()
