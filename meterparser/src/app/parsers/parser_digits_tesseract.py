
# import pytesseract

# # tesseract code for when we have good trained data
# def ocr_tesseract(frame, digits_count, decimals_count, entity_id):
#     reading = 0
#     try:
#         _LOGGER.debug("Sending frame to tesseract %s" % (pytesseract.get_tesseract_version()))
        
#         text = pytesseract.image_to_string(frame, lang="digits_comma", config="--psm 7 -c tessedit_char_whitelist=0123456789", timeout=15)
#         reading = parse_result(
#                 text,
#                 digits_count,
#                 decimals_count,
#                 entity_id,
#             )
#     except Exception as e:
#         _LOGGER.debug("Error while OCR with tesseract: %s" % e)
#     return reading