/* 
 * Profiler -> routes -> main.js
 * ----------------------------------------------------------------------------------------------------
 * 
 * Author: Ronnie Smith <ronnie.smith@ed.ac.uk / ras35@hw.ac.uk>
 * Version: 1.0
 * Date: 25th February 2019
 * 
 */

/* 
 * Defintions and Global Variables
 * ----------------------------------------------------------------------------------------------------
 */

// Express
var express = require('express');
var router = express.Router();
var bodyParser = require('body-parser');
router.use(bodyParser.urlencoded({ extended: true }));

// MongoDB
var dbName = "AR";
var mongo = require('mongodb');
var mongoClient = require('mongodb').MongoClient;
var db = require('mongodb').Db;
var con_url = "mongodb://localhost:27017/" + dbName;

router.get('/', function (req, res, next) {
    res.render('index', { title: 'Hello, World!' })
})
  
router.get('/nameOfGet', function (req, res, next) {

    mongoClient.connect(con_url, function(err, db){
        if(err) throw err;
        db.collection('People').find().limit(1).sort({$natural:-1}).toArray(function(err, docs) {
            console.log(JSON.stringify(docs));
            db.close();

            if (docs) {
                res.status(200)
                res.json({
                    success: true,
                    message: 'Last person added.',
                    location: docs
                })
            } else {
                res.status(404)
                res.json({
                    success: false,
                    message: 'Unable to retrieve last person added.'
                })
            }

        });
    });
  })

  module.exports = router

  /* 
 * DB Manipulation Functions  
 * ----------------------------------------------------------------------------------------------------
 */

function addPerson(data){

    mongoClient.connect(con_url, function(err, db){
        if(err) throw err;
        db.collection("People").insert(data, function(err, res) {
            if (err) throw err;
            console.log("Added 1 person to People collection.");
            db.close();
        });
    });

}

function retrievePerson(data){

    mongoClient.connect(con_url, function(err, db){
        if(err) throw err;
        db.collection("People").find().toArray(function(err, docs) {
            console.log(JSON.stringify(docs));
            db.close();
        });
    });

}