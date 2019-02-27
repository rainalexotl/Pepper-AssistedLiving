var mongoose = require('mongoose')
var uniqueValidator = require('mongoose-unique-validator')
var Schema = mongoose.Schema

/*
 * Schema
 * ----------------------------------------------------------------------------------------------------
 */

var BackgroundSchema = new Schema({
  eyeColour: { type: String, required: false, default: "unknown" },
  formerProfession: { type: String, required: false, default: "unknown" },
  favouriteAnimal: { type: String, required: false, default: "unknown" },
  numChildren: { type: String, required: false, default: "unknown" },
  birthplace: { type: String, required: false, default: "unknown" }
})

var LikesDislikesSchema = new Schema({
  type: { type: String, required: false },
  likeDislike: { type: Boolean, required: false },
  thing: { type: String, required: false }
})

var PersonSchema = new Schema({
  forename: { type: String, required: true },
  surname: { type: String, required: true },
  background: {type: BackgroundSchema, default: BackgroundSchema },
  likesDislikes: [LikesDislikesSchema]
})

PersonSchema.plugin(uniqueValidator)

var PersonModel = mongoose.model('Person', PersonSchema)

PersonModel.prototype.tolistJSON = function () {
  return {
    id: this._id,
    title: this.title
  }
}

if (!PersonSchema.options.toJSON) PersonSchema.options.toJSON = {}
PersonSchema.options.toJSON.transform = function (doc, ret, options) {
  ret.id = ret._id
  delete ret._id
  return ret
}

module.exports = PersonModel
