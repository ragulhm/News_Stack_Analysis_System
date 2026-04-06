async function analyze() {
    const company = document.getElementById("company").value;

    document.getElementById("results").innerHTML = "Loading...";

    const response = await fetch(`/analyze/${company}`);
    const data = await response.json();

    let output = "";

    data.forEach(item => {

        let color = "white";

        if (item.sentiment === "positive") color = "lightgreen";
        if (item.sentiment === "negative") color = "red";

        output += `
        <div class="card">
            <h3>${item.title}</h3>
            <p style="color:${color}">Sentiment: ${item.sentiment}</p>
            <p>${item.signal}</p>
        </div>
        `;
    });

    document.getElementById("results").innerHTML = output;
}