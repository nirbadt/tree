require('dotenv').config()

const redis = require('redis')
const client = redis.createClient({
    host: process.env.REDIS_HOST,
    password: process.env.REDIS_AUTH
})

client.on('error', function (err) {
    console.error('Error ' + err);
});

client.monitor(function (err, res) {
    console.log('Entering monitoring mode.');
});

client.on('monitor', function (time, args, raw_reply) {
    console.log(`${time}: ${args}`);
});