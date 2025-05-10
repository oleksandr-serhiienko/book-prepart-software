// This script converts from messages format to contents format
const fs = require('fs');

// Function to transform the data format
function transformFormat(content) {
  // Split the content by newlines and filter out empty lines
  const jsonStrings = content.split('\n').filter(line => line.trim());
  
  // Array to store the transformed objects
  const transformedObjects = [];
  
  for (const jsonStr of jsonStrings) {
    try {
      const jsonObj = JSON.parse(jsonStr);
      
      // Check if this is in the messages format
      if (jsonObj.messages && Array.isArray(jsonObj.messages)) {
        // Find the user and assistant messages
        const userMsg = jsonObj.messages.find(msg => msg.role === 'user');
        const assistantMsg = jsonObj.messages.find(msg => msg.role === 'assistant');
        
        if (userMsg && assistantMsg) {
          // Create the new format
          const transformedObj = {
            "contents": [
              {
                "role": "user",
                "parts": [
                  {
                    "text": userMsg.content
                  }
                ]
              },
              {
                "role": "model",
                "parts": [
                  {
                    "text": assistantMsg.content
                  }
                ]
              }
            ]
          };
          
          transformedObjects.push(JSON.stringify(transformedObj));
        }
      }
    } catch (error) {
      console.error('Error processing JSON object:', error.message);
      // Continue to the next line
    }
  }
  
  return transformedObjects.join('\n');
}

// Read and process the file
function processFile() {
  try {
    // Check if command line arguments are provided
    const args = process.argv.slice(2);
    let inputPath, outputPath;
    
    if (args.length >= 2) {
      inputPath = args[0];
      outputPath = args[1];
    } else {
      // Default paths
      inputPath = 'C:/Users/Serhi/OneDrive/Desktop/evaluate-train-word-de-en-new.txt';
      outputPath = 'C:/Users/Serhi/OneDrive/Desktop/transformed_word_data_evaluate.jsonl';
    }
    
    console.log(`Reading from: ${inputPath}`);
    console.log(`Writing to: ${outputPath}`);
    
    // Read the input file
    const fileContent = fs.readFileSync(inputPath, 'utf8');
    
    // Transform the data
    const transformedContent = transformFormat(fileContent);
    
    // Write the output file
    fs.writeFileSync(outputPath, transformedContent, 'utf8');
    
    // Count how many objects were processed
    const objectCount = transformedContent.split('\n').filter(line => line.trim()).length;
    
    console.log(`Transformation completed. Output written to ${outputPath}`);
    console.log(`Processed ${objectCount} objects.`);
  } catch (error) {
    console.error('Error processing file:', error.message);
    process.exit(1);
  }
}

// Run the script
processFile();