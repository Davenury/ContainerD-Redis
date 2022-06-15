const express = require('express');
const bodyParser = require('body-parser');
const fs = require('fs');

const app = express();
app.use(bodyParser.json());


const stats = ["Ops/sec","Hits/sec","Misses/sec","Latency","KB/sec"]


const writeResult = (cpu, type, result) => {

    const sets = result["ALL STATS"][type]

    const setsArray = [cpu, ...stats.map(elem => sets[elem])]

    try {
        fs.appendFileSync('./result.csv', [...setsArray, type].join(','));
        fs.appendFileSync('./result.csv', "\n");
        // file written successfully
    } catch (err) {
        console.error(err);
    }

}

const writeRedisBenchmarkResult = (cpu, result) => {
    fs.writeFileSync(`./result${cpu}.csv`, "operation,ops\n")
    result.forEach(element => {
        fs.writeFileSync(`./result${cpu}.csv`, `${element["operation"]},${element["ops"]}\n`)
    });
}


app.post('/:cpu/:type', (req, res) => {
    writeResult(req.params["cpu"], req.params["type"], req.body);
    res.sendStatus(200);
});

app.post('/redis-benchmark/:cpu', (req, res) => {
    writeRedisBenchmarkResult(req.params["cpu"], req.body);
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