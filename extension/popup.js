document.getElementById('analyze-btn').addEventListener('click', async () => {
    // Show loading
    document.getElementById('loading').style.display = 'block';
    document.getElementById('result').style.display = 'none';

    try {
        // Query active tab to get highlighted text
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        
        chrome.scripting.executeScript({
            target: { tabId: tab.id },
            function: () => window.getSelection().toString()
        }, async (injectionResults) => {
            const selectedText = injectionResults[0].result;
            
            if (!selectedText || selectedText.trim().length < 10) {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('result').style.display = 'block';
                document.getElementById('prediction').textContent = "Please highlight a paragraph of text first.";
                document.getElementById('prediction').className = "";
                document.getElementById('confidence').textContent = "";
                document.getElementById('result').style.border = "1px solid #64748b";
                return;
            }

            // Send to TruthSense backend
            // In a real deployed app, change localhost to the deployed URL
            const response = await fetch('http://localhost:5000/api/v1/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    text: selectedText,
                    title: "Extension Analysis"
                })
            });

            const data = await response.json();
            
            document.getElementById('loading').style.display = 'none';
            const resultDiv = document.getElementById('result');
            resultDiv.style.display = 'block';
            
            const predictionEl = document.getElementById('prediction');
            predictionEl.textContent = data.prediction;
            predictionEl.className = data.prediction === 'RELIABLE' ? 'reliable' : 'unreliable';
            
            // Apply styling
            if(data.prediction === 'RELIABLE') {
                resultDiv.className = 'reliable';
            } else {
                resultDiv.className = 'unreliable';
            }
            
            document.getElementById('confidence').textContent = `Confidence: ${Math.round(data.confidence * 100)}%`;
        });
    } catch (err) {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('prediction').textContent = "Connection failed. Is TruthSense running?";
        document.getElementById('result').style.display = 'block';
        console.error("Error:", err);
    }
});
