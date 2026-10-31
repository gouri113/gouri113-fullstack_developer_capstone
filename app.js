const express = require('express');
const mongoose = require('mongoose');
const fs = require('fs');
const cors = require('cors');

const app = express();
const port = 3030;

app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: false }));

// Resolve seed data file paths (works both inside container and on host)
const reviews_file = fs.existsSync("reviews.json") ? "reviews.json" : "./data/reviews.json";
const dealerships_file = fs.existsSync("dealerships.json") ? "dealerships.json" : "./data/dealerships.json";

const reviews_data = JSON.parse(fs.readFileSync(reviews_file, 'utf8'));
const dealerships_data = JSON.parse(fs.readFileSync(dealerships_file, 'utf8'));

const Reviews = require('./review');
const Dealerships = require('./dealership');

// Connect to MongoDB (tries external/container MongoDB first, falls back to local engine)
async function connectAndSeedDB() {
  const defaultUrl = process.env.MONGO_URL || "mongodb://127.0.0.1:27017/dealershipsDB";
  try {
    await mongoose.connect(defaultUrl, { serverSelectionTimeoutMS: 2000 });
    console.log(`Connected to MongoDB at ${defaultUrl}`);
  } catch (err) {
    console.log("Could not reach external MongoDB server, starting local MongoDB engine...");
    const { MongoMemoryServer } = require('mongodb-memory-server');
    const mongod = await MongoMemoryServer.create({
      instance: {
        port: 27017,
        dbName: 'dealershipsDB'
      }
    });
    const memoryUri = mongod.getUri();
    await mongoose.connect(memoryUri, { dbName: 'dealershipsDB' });
    console.log(`Connected to local MongoDB engine at ${memoryUri}`);
  }

  try {
    await Reviews.deleteMany({});
    await Reviews.insertMany(reviews_data['reviews']);
    await Dealerships.deleteMany({});
    await Dealerships.insertMany(dealerships_data['dealerships']);
    console.log("Database seeded successfully with dealerships and reviews.");
  } catch (seedErr) {
    console.error("Error seeding initial data:", seedErr);
  }
}

connectAndSeedDB();

// Express route to home
app.get('/', async (req, res) => {
  res.send("Welcome to the Mongoose API");
});

// Express route to fetch all reviews
app.get('/fetchReviews', async (req, res) => {
  try {
    const documents = await Reviews.find();
    res.json(documents);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching documents' });
  }
});

// Express route to fetch reviews by a particular dealer
app.get('/fetchReviews/dealer/:id', async (req, res) => {
  try {
    const documents = await Reviews.find({ dealership: parseInt(req.params.id) });
    res.json(documents);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching documents' });
  }
});

// Express route to fetch all dealerships
app.get('/fetchDealers', async (req, res) => {
  try {
    const documents = await Dealerships.find();
    res.json(documents);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching dealerships' });
  }
});

// Express route to fetch Dealers by a particular state
app.get('/fetchDealers/:state', async (req, res) => {
  try {
    const documents = await Dealerships.find({ state: req.params.state });
    res.json(documents);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching dealerships by state' });
  }
});

// Express route to fetch dealer by a particular id
app.get('/fetchDealer/:id', async (req, res) => {
  try {
    const documents = await Dealerships.find({ id: parseInt(req.params.id) });
    res.json(documents);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching dealer by id' });
  }
});

// Express route to insert review
app.post('/insert_review', express.raw({ type: '*/*' }), async (req, res) => {
  try {
    let data;
    if (Buffer.isBuffer(req.body)) {
      data = JSON.parse(req.body.toString('utf8'));
    } else if (typeof req.body === 'string') {
      data = JSON.parse(req.body);
    } else {
      data = req.body;
    }

    const documents = await Reviews.find().sort({ id: -1 });
    let new_id = (documents.length > 0 && documents[0]['id']) ? documents[0]['id'] + 1 : 1;

    const review = new Reviews({
      "id": new_id,
      "name": data['name'],
      "dealership": parseInt(data['dealership']),
      "review": data['review'],
      "purchase": Boolean(data['purchase']),
      "purchase_date": data['purchase_date'] || new Date().toISOString(),
      "car_make": data['car_make'],
      "car_model": data['car_model'],
      "car_year": data['car_year'] ? parseInt(data['car_year']) : 2023,
    });

    const savedReview = await review.save();
    res.json(savedReview);
  } catch (error) {
    console.error("Error inserting review:", error);
    res.status(500).json({ error: 'Error inserting review' });
  }
});

// Start the Express server
app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
