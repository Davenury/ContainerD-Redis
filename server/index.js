const express = require('express');
const bodyParser = require('body-parser');
const fs = require('fs');

const app = express();
app.use(bodyParser.json());


const stats = ["Ops/sec","Hits/sec","Misses/sec","Latency","KB/sec"]


const writeResult = (cpu, result) => {

    const sets = result["ALL STATS"]["Sets"]
    const gets = result["ALL STATS"]["Gets"]

    const setsArray = [cpu, ...stats.map(elem => sets[elem])]
    const getsArray = [cpu, ...stats.map(elem => gets[elem])]

    try {
        fs.appendFileSync('./result.csv', [...setsArray, "sets"].join(','));
        fs.appendFileSync('./result.csv', "\n");
        fs.appendFileSync('./result.csv', [...getsArray, "gets"].join(','));
        fs.appendFileSync('./result.csv', "\n");
        // file written successfully
    } catch (err) {
        console.error(err);
    }

}


app.post('/:cpu', (req, res) => {
    writeResult(req.params["cpu"], req.body);
    res.sendStatus(200);
});

app.listen(8080, () => {
    try {
        fs.writeFileSync("./result.csv", ["CPU Percentage", ...stats, "Operation"].join(','));
        fs.appendFileSync('./result.csv', "\n");
    } catch(err) {
        console.error(err)
    }
    console.log(`Started server at http://localhost:8080!`)
});