var express = require('express')
var app = express()
var path = require('path')
var favicon = require('serve-favicon')
var logger = require('morgan')
var cookieParser = require('cookie-parser')
var bodyParser = require('body-parser')
var morgan = require('morgan')
var MongoClient = require('mongodb').MongoClient
var mongoose = require('mongoose')
var db = require('mongodb').Db
var conn_url = 'mongodb://localhost:27017/admin'

// Requirements -> Auth
var config = require('./config') // get our config file

// Requirements -> Routing
var index = require('./routes/index')
var person = require('./routes/person')

/*
 * MongoClient
 * ----------------------------------------------------------------------------------------------------
 */

MongoClient.connect(conn_url, function (err, db) {
  if (err) throw err

  // view engine setup
  app.set('views', path.join(__dirname, 'views'))
  app.set('view engine', 'jade')

  app.use(logger('dev'))
  app.use(bodyParser.json())
  app.use(bodyParser.urlencoded({ extended: true }))
  app.use(cookieParser())
  app.use(express.static(path.join(__dirname, 'public')))

  app.use(function (req, res, next) {
    var err = new Error('Not Found')
    err.status = 404
    next(err)
  })

  app.use(function (err, req, res, next) {
    res.locals.message = err.message
    res.locals.error = req.app.get('env') === 'development' ? err : {}
    res.status(err.status || 500)
    res.render('error')
  })
})

module.exports = app

// Configuration
var port = process.env.PORT || 3010
mongoose.connect(config.database)
app.set('secret', config.secret)

app.use(logger('dev'))
app.use(bodyParser.json())
app.use(cookieParser())
app.use(express.static(path.join(__dirname, 'public')))
app.use(bodyParser.urlencoded({ extended: false }))
app.use(bodyParser.json())

app.use(morgan('dev'))

// Routing
app.use('/api/person', person)

// Launch
app.listen(port)
console.log('Profiler is running..')
