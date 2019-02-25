const express = require('express')
const router = express.Router()
const mongoose = require('mongoose')

const Person = require('../models/person')

const handleError = error => {
  return console.log(error)
}

// Test
router.get('/test', function (req, res, next) {
  res.header('Location', `/api/person/test`)
  res.status(201)
  res.json({
    success: true,
    message: 'Hello, World',
  })
})

// Create new user
router.post('/', function (req, res, next) {
  const p = new Person()

  p.name = req.body.name

  p.save(function (err, newPerson) {
    if (err) {
      res.status(400)
      return res.json({
        success: false,
        message: err.message
      })
    }

    res.header('Location', `/api/person/addPerson`)
    res.status(201)
    res.json({
      success: true,
      message: 'New Person Added',
      person: newPerson.toJSON()
    })
  })
})

// Add likes
router.post('/likeDislike', function (req, res, next) {

  Person.findOne({ name: req.body.name }, function (err, person){
    var newLikeDislike = { likeDislike: req.body.likeDislike, thing: req.body.thing}
    
    person.likesDislikes.push(newLikeDislike)

    console.log(person)
    person.save(function (err, p) {
      if (err) {
        res.status(400)
        return res.json({
          success: false,
          message: err.message
        })
      }
  
      res.header('Location', `/api/person/likeDislike`)
      res.status(201)
      res.json({
        success: true,
        message: 'New Like/Dislike Added',
        person: p.toJSON()
      })
    })
  });

})

module.exports = router
