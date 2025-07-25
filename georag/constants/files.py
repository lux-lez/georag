# Recognized document formats 
MediaCategories = {
    "text" :        ['.txt', '.md'],                           
    "document" :    ['.pdf', '.doc', '.docx', ".odt"],   
    "video" :       [".mov", ".avi", ".mp4"],         
    "audio" :       [".mp3", ".wav", ".flac"],
    "archive" :     ['.zip', '.rar', '.7z'],                       
    "image" :       ['.png', '.jpg', '.jpeg', '.svg']                
}

# Settings for handling file categories
MediaRules = {
    "text" :        "save",
    "document" :    "save",
    "image" :       "ignore",
    "archive" :     "ignore",
}

AllowedDocumentExtensions = [
    ".md", ".txt", ".pdf", 
]