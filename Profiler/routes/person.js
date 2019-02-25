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
router.post('/add', function (req, res, next) {
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

    res.header('Location', `/api/person/add`)
    res.status(201)
    res.json({
      success: true,
      message: 'New Person Added',
      person: newPerson.toJSON()
    })
  })
})

module.exports = router
