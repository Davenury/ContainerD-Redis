const express = require('express');
const bodyParser = require('body-parser');
const fs = require('fs');

const app = express();
app.use(bodyParser.json());


const stats = ["Ops/sec","Hits/sec","Misses/sec","Latency","KB/sec"]


const writeResult = (cpu, type, instance_type, result) => {

    const sets = result["ALL STATS"][type]

    const setsArray = [cpu, ...stats.map(elem => sets[elem])]

    try {
        fs.appendFileSync('./results/result.csv', [...setsArray, type, instance_type].join(','));
        fs.appendFileSync('./results/result.csv', "\n");
        // file written successfully
    } catch (err) {
        console.error(err);
    }

}

const writeRedisBenchmarkResult = (cpu, result) => {
    fs.writeFileSync(`./results/redis_result${cpu}.csv`, "operation,ops\n")
    result.forEach(element => {
        fs.writeFileSync(`./results/redis_result${cpu}.csv`, `${element["operation"]},${element["ops"]}\n`)
    });
}


app.post('/:cpu/:operation_type/:instance_type', (req, res) => {
    writeResult(req.params["cpu"], req.params["operation_type"], req.params["instance_type"], req.body);
    res.sendStatus(200);
});

app.post('/redis-benchmark/:cpu', (req, res) => {
    writeRedisBenchmarkResult(req.params["cpu"], req.body);
    res.sendStatus(200);
});

app.listen(8080, () => {
    try {
        fs.mkdirSync("results")
        fs.writeFileSync("./results/result.csv", ["CPU Percentage", ...stats, "Operation", "Instance type"].join(','));
        fs.appendFileSync('./results/result.csv', "\n");
    } catch(err) {
        console.error(err)
    }
    console.log(`Started server at http://localhost:8080!`)
});