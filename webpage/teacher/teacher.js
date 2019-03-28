init = () => {
    // Run it at first
    requestPresent();
    requestUnclaimed();
    // Set the intervals until forever
    setInterval(requestPresent, 3000);
    setInterval(requestUnclaimed, 3000);
}

requestNewDbEntry = () => {
    // No validation necessary for this function since we assume
    // the teacher is not malicious
    let xml = new XMLHttpRequest();
    xml.onreadystatechange = function() {
        if (this.status === 200 && this.readyState === 4) {
            // Success, print the secret to the status div
            document.getElementById("status").innerHTML = this.responseText;
        }
    }
    // Call our create_new_db_entry.php endpoint
    xml.open("POST", "create_new_db_entry.php");
    // We have to set the header since we don't have anything else controlling it
    xml.setRequestHeader("content-type", "application/x-www-form-urlencoded");
    // Send the payload with requestSecret
    xml.send("requestSecret=true");
}

requestPresent = () => {
    let xml = new XMLHttpRequest();
    xml.onreadystatechange = function () {
        if (this.status === 200 && this.readyState === 4) {
            // Success, thus build the table
            let body = tableHelper(["Student ID", "Name", "Photo"], JSON.parse(this.responseText));
            document.getElementById("tablePresent").innerHTML = body;
        }
    }
    // Call our create_new_db_entry.php endpoint
    xml.open("POST", "request_db_entries.php");
    // We have to set the header since we don't have anything else controlling it
    xml.setRequestHeader("content-type", "application/x-www-form-urlencoded");
    // Send the payload with requestSecret
    xml.send("requestTable=present");
}

requestUnclaimed = () => {
    let xml = new XMLHttpRequest();
    xml.onreadystatechange = function () {
        if (this.status === 200 && this.readyState === 4) {
            // Success, thus build the table
            let body = tableHelper(["Unclaimed Secrets"], JSON.parse(this.responseText));
            document.getElementById("tableUnclaimed").innerHTML = body;
        }
    }
    // Call our create_new_db_entry.php endpoint
    xml.open("POST", "request_db_entries.php");
    // We have to set the header since we don't have anything else controlling it
    xml.setRequestHeader("content-type", "application/x-www-form-urlencoded");
    // Send the payload with requestSecret
    xml.send("requestTable=unclaimed");
}

/**
 * This helper takes in an array of headers, and a JSON
 * to create the table HTML elements. Must ensure that 
 * json.length == headers.length. Does not check malformity
 */
tableHelper = (headers, json) => {
    let body = "<table class='table table-light'><thead><tr>";
    for (let i = 0; i < headers.length; i++) {
        body += "<th scope='col'>" + headers[i] + "</th>";
    }
    body += "</tr></thead><tbody>";
    for (let i = 0; i < json.length; i++) {
        body += "<tr>";
        for (let j = 0; j < json[i].length; j++) {
            body += "<td>";
            if (headers[j] === "Photo") {
                body += specialImageHandler(json[i][j]);
            } else {
                body += json[i][j];
            }
            body += "</td>";
        }
        body += "</tr>";
    }
    body += "</tbody>";
    body += "</table>";
    return body;
}

specialImageHandler = (filename) => {
    return "<a>Hover<div class='imgContainer'><img src=/photos/" + filename
                    + "?></div></a>";
}