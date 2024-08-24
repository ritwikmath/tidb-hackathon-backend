document.addEventListener('DOMContentLoaded', function () {
    const modeRadioButtons = document.querySelectorAll('input[name="mode"]');
    const generalSQLForm = document.getElementById('generalSQL');
    const textToSQLForm = document.getElementById('textToSQL');

    modeRadioButtons.forEach(radio => {
        radio.addEventListener('change', function () {
            if (this.value === 'general') {
                generalSQLForm.style.display = 'block';
                textToSQLForm.style.display = 'none';
            } else if (this.value === 'textToSQL') {
                generalSQLForm.style.display = 'none';
                textToSQLForm.style.display = 'block';
            }
        });
    });
});

document.addEventListener('DOMContentLoaded', function () {
    const queryForm = document.getElementById('queryForm');
    const apiResponseDiv = document.getElementById('apiResponse');
    const loader = document.getElementById('loader');

    queryForm.addEventListener('submit', async function (event) {
        event.preventDefault(); // Prevent the form from submitting the traditional way

        // Show the loader
        loader.style.visibility = 'visible';

        // Determine which radio button is selected
        const selectedMode = document.querySelector('input[name="mode"]:checked').value;

        let apiUrl;
        let requestData = {};

        if (selectedMode === 'general') {
            apiUrl = '/sql-query-response';
            requestData.schema = document.getElementById('schema').value;
            requestData.question = document.getElementById('questionGeneral').value;
        } else if (selectedMode === 'textToSQL') {
            apiUrl = '/sql-text-to-query';
            requestData.question = document.getElementById('questionTextToSQL').value;
        }

        try {
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();

            // Display the API response in the right-side div
            let converter = new showdown.Converter()
            apiResponseDiv.innerHTML = converter.makeHtml(data.message);
        } catch (error) {
            apiResponseDiv.textContent = `Error: ${error.message}`;
        } finally {
            loader.style.visibility = 'hidden';
        }
    });
});

