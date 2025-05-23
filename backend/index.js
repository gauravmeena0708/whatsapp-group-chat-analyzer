const express = require('express');
const multer = require('multer');
const cors = require('cors');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const app = express();
const port = 3000;

// Enable CORS for all routes
app.use(cors());

// --- Multer Configuration for File Uploads ---
const uploadsDir = path.join(__dirname, 'uploads');
// Ensure the uploads directory exists
if (!fs.existsSync(uploadsDir)) {
    fs.mkdirSync(uploadsDir, { recursive: true });
    console.log(`Created directory: ${uploadsDir}`);
}

const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        cb(null, uploadsDir);
    },
    filename: function (req, file, cb) {
        // Use a timestamp or a unique ID generator for more robust unique filenames
        const uniquePrefix = Date.now() + '-' + Math.round(Math.random() * 1E9);
        cb(null, uniquePrefix + '-' + file.originalname);
    }
});
const upload = multer({ storage: storage });

// --- API Endpoints ---

// Basic status endpoint
app.get('/api/status', (req, res) => {
    res.json({ status: 'Backend is running and ready to analyze!' });
});

// Endpoint to handle chat file analysis
app.post('/api/analyze', upload.single('chatfile'), (req, res) => {
    if (!req.file) {
        return res.status(400).json({ error: 'No file uploaded. Please upload a .txt chat file.' });
    }

    const uploadedFilePath = req.file.path;
    const originalFileName = req.file.originalname;
    const analysesStringFromFrontend = req.body.analyses; // Get analyses string from request body

    // Create a base directory for all analysis results if it doesn't exist
    const baseOutputDir = path.join(__dirname, 'analysis_results');
    if (!fs.existsSync(baseOutputDir)) {
        fs.mkdirSync(baseOutputDir, { recursive: true });
        console.log(`Created base output directory: ${baseOutputDir}`);
    }
    
    // Create a unique temporary directory for this analysis's results
    let outputDir;
    try {
        outputDir = fs.mkdtempSync(path.join(baseOutputDir, `analysis-${Date.now()}-`));
        console.log(`Created temporary output directory: ${outputDir}`);
    } catch (err) {
        console.error('Error creating temporary output directory:', err);
        return res.status(500).json({ error: 'Failed to create temporary directory for analysis results.' });
    }

    const pythonScriptPath = path.resolve(__dirname, '../src/whatsapptools/groupanalyzer.py');
    const pythonExecutable = 'python3';

    // Prepare arguments for the Python script
    const pythonArgs = [
        pythonScriptPath,
        '--input_file',
        uploadedFilePath,
        '--output_dir',
        outputDir
    ];

    if (analysesStringFromFrontend && analysesStringFromFrontend.trim() !== "") {
        pythonArgs.push('--analyses', analysesStringFromFrontend);
        console.log(`Passing selected analyses to Python script: ${analysesStringFromFrontend}`);
    } else {
        console.log('No specific analyses selected by frontend, Python script will use its defaults.');
        // If analysesStringFromFrontend is empty or undefined, 
        // groupanalyzer.py will use its own default for --analyses.
    }

    console.log(`Executing Python script: ${pythonExecutable} ${pythonArgs.join(' ')}`);
    console.log(`Input file: ${uploadedFilePath}`);
    console.log(`Output directory: ${outputDir}`);

    const pythonProcess = spawn(pythonExecutable, pythonArgs);

    let scriptOutput = '';
    let scriptError = '';

    pythonProcess.stdout.on('data', (data) => {
        scriptOutput += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
        scriptError += data.toString();
        console.error(`Python stderr: ${data}`);
    });

    pythonProcess.on('close', (code) => {
        console.log(`Python script exited with code ${code}`);

        // Optionally, clean up the uploaded file after processing
        // fs.unlink(uploadedFilePath, (unlinkErr) => {
        //     if (unlinkErr) console.error('Error deleting uploaded file:', unlinkErr);
        //     else console.log('Uploaded file deleted successfully.');
        // });

        if (code !== 0 || (scriptError && !scriptError.toLowerCase().includes("nltk data server"))) { // Ignore NLTK download messages in stderr for error check
            const errorMessage = scriptError || `Python script execution failed with code ${code}.`;
            console.error('Python script error:', errorMessage);
            return res.status(500).json({ 
                error: 'Error during chat analysis.', 
                details: errorMessage,
                rawOutput: scriptOutput 
            });
        }
        
        // If scriptError contains only NLTK download messages, it's not a true error for the response.
        if (scriptError && scriptError.toLowerCase().includes("nltk data server") && code === 0) {
            console.log("NLTK data download messages were present in stderr, but script succeeded.");
        }


        try {
            let analysisResult = JSON.parse(scriptOutput);
            
            const transformedAnalysisResult = {};
            for (const key in analysisResult) {
                if (analysisResult.hasOwnProperty(key) && typeof analysisResult[key] === 'string') {
                    const absolutePath = analysisResult[key];
                    if (absolutePath.startsWith(baseOutputDir)) {
                        transformedAnalysisResult[key] = path.relative(__dirname, absolutePath);
                    } else {
                        transformedAnalysisResult[key] = analysisResult[key]; 
                        console.warn(`Path ${absolutePath} for key ${key} does not start with baseOutputDir ${baseOutputDir}. Using original path.`);
                    }
                } else {
                    transformedAnalysisResult[key] = analysisResult[key]; 
                }
            }

            res.json({ 
                message: `File '${originalFileName}' analyzed successfully.`,
                analysis: transformedAnalysisResult
            });
        } catch (parseError) {
            console.error('Error parsing Python script output:', parseError);
            console.error('Raw Python output:', scriptOutput);
            return res.status(500).json({ 
                error: 'Error parsing analysis results.', 
                details: parseError.message,
                rawOutput: scriptOutput 
            });
        }
    });

    pythonProcess.on('error', (err) => {
        console.error('Failed to start Python process:', err);
        // fs.unlink(uploadedFilePath, () => {}); 
        return res.status(500).json({ error: 'Failed to start analysis process.', details: err.message });
    });
});


// --- Route to serve generated analysis files ---
app.get('/api/analysis_results/:analysisId/:filename', (req, res) => {
    const { analysisId, filename } = req.params;

    const analysisIdPattern = /^analysis-\d{13}-[a-zA-Z0-9]+$/; 
    if (!analysisIdPattern.test(analysisId) || analysisId.includes('..') || analysisId.includes('/') || analysisId.includes('\\')) {
        return res.status(400).json({ error: 'Invalid analysis ID format.' });
    }

    if (filename.includes('..') || filename.includes('/') || filename.includes('\\')) {
        return res.status(400).json({ error: 'Invalid filename format.' });
    }

    const resultsBaseDir = path.join(__dirname, 'analysis_results');
    const filePath = path.join(resultsBaseDir, analysisId, filename);
    const resolvedFilePath = path.resolve(filePath); 

    if (!resolvedFilePath.startsWith(path.resolve(resultsBaseDir))) {
        console.error(`Attempted directory traversal: ${analysisId}/${filename}`);
        return res.status(403).json({ error: 'Forbidden: Access denied.' });
    }
    
    fs.access(resolvedFilePath, fs.constants.F_OK, (err) => {
        if (err) {
            console.error(`File not found or not accessible: ${resolvedFilePath}`, err);
            return res.status(404).json({ error: 'File not found.' });
        }

        if (path.extname(filename).toLowerCase() === '.csv') {
            res.setHeader('Content-Disposition', 'attachment; filename="' + filename + '"');
        }
        
        res.sendFile(resolvedFilePath, (sendFileErr) => {
            if (sendFileErr) {
                console.error(`Error sending file ${resolvedFilePath}:`, sendFileErr);
                if (!res.headersSent) {
                    res.status(500).json({ error: 'Error sending file.' });
                }
            }
        });
    });
});


app.listen(port, () => {
    console.log(`Backend server listening at http://localhost:${port}`);
});
