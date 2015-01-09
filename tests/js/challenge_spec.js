describe('challenge', function () {

    var browserType;
    var login, password, opponent = null;
    var game_id = 4;
    var pr;

    beforeEach(function () {

        browser.getCapabilities().then(function (cap) {
            browserType = cap.caps_.browserName;
            if (browserType == 'firefox') {
                login = 'vit';
                password = '123';
                opponent = 'test';
            } else {
                login = 'test';
                password = 'test';
                opponent = 'vit';
            }

            pr = protractor.getInstance();
        });

    });

    it('user login', function () {
        browser.ignoreSynchronization = true;
        browser.get('http://127.0.0.1:8000/4/accounts/login/');

        expect(browser.getTitle()).toEqual('Login');

        element(by.id('id_username')).sendKeys(login);
        element(by.id('id_password')).sendKeys(password);
        element(by.id('btn-login')).click();

        expect(browser.getTitle()).toEqual('Challenge');
        browser.ignoreSynchronization = false;
    });

    it('we on main screen', function () {
        browser.get('http://127.0.0.1:8000/4/core/#/multi/')
        browser.debugger();
        expect(browser.getTitle()).toEqual('Challenge');
        expect(browser.getLocationAbsUrl()).toEqual('http://127.0.0.1:8000/4/core/#/multi/')
    });

    it('go to server screen', function () {
        element(by.css('div.list-group a:nth-child(2)')).click();
        expect(browser.getLocationAbsUrl()).toEqual('http://127.0.0.1:8000/4/core/#/multi/server/')
    });


    it('we should see each other', function () {
        pr.wait(function () {
            return element.all(by.repeater('u in onlineUsers')).count().then(function (val) {
                return val == 1;
            })
        }, 4000, 'No online users...')

        var elems = element.all(by.repeater('u in onlineUsers'));

        expect(elems.count()).toBe(1);
    });

    it('check name of opponent', function () {
        var elems = element.all(by.repeater('u in onlineUsers'));
        expect(elems.first().element(by.css('.player_username')).getText()).toBe(opponent)
    })

    it('make an invite from firefox', function () {
        var elems = element.all(by.repeater('u in onlineUsers'));

        if (browserType == 'firefox') {
            // no betting screen
            expect(element(by.css('div.betting')).isDisplayed()).toBe(false);

            // clck on username
            elems.first().element(by.css('a')).click();

            // show betting screen
            expect(element(by.css('div.betting')).isDisplayed()).toBe(true);

            // another user is still here
            expect(elems.count()).toBe(1);

            expect(element(by.binding('mybets')).getText()).toBe('10');

            // click on '+ 10'
            element(by.css('div.betting .increase-gumballs')).click();

            expect(element(by.binding('mybets')).getText()).toBe('20');

            // click 'submit'
            element(by.css('div.betting .confirm-gumballs')).click();

            pr.wait(function() {
                return element(by.css('div.connecting_to_unity')).isDisplayed().then(function (val) {
                    return val;
                })

            }, 3000, 'A long waiting for connecting_to_unity, firefox')

            console.log('CONNECTING TO UNITY - FIREFOX');

            browser.executeScript(function() {
                angular.element(document.getElementById("index_ctrl")).scope().xRecievedJson();
            });

            pr.wait(function() {
                return element(by.css('span.step2')).isDisplayed().then(function (val) {
                    return val;
                })

            }, 3000, 'A long waiting for step2, firefox')


            browser.executeScript(function() {
                var guid = angular.element(document.getElementById("index_ctrl")).scope().challenge.guid;

                angular.element(document.getElementById("index_ctrl")).scope().xSetServerStatus(
                    {"challenge":guid,"type":"p2p","result":"SUCCess"}
                );
            });

            pr.wait(function() {
                return element(by.css('span.step4')).isDisplayed().then(function (val) {
                    return val;
                })

            }, 5000, 'A long waiting for step4 - playing, firefox')




        } else {
            // CHROME
            // waiting for an invite
            pr.wait(function () {
                return element(by.css('div.answering')).isDisplayed().then(function (val) {
                    return val;
                })
            }, 3000, 'A long waiting for answering, chrome')


            console.log('ANSWERING - CHROME');
            expect(element(by.css('span.gumballs_count')).getText()).toBe('20');

            element(by.css('.accept_invite')).click();

            expect(element(by.css('div.answering')).isDisplayed()).toBe(false);

            pr.wait(function() {
                return element(by.css('div.connecting_to_unity')).isDisplayed().then(function (val) {
                    return val;
                })

            }, 3000, 'A long waiting for connecting_to_unity, chrome')

            console.log('CONNECTING TO UNITY - CHROME');

            // emulation a request from Unity
            browser.executeScript(function() {
                angular.element(document.getElementById("index_ctrl")).scope().xRecievedJson();
            });

            // waiting...
            pr.wait(function() {
                return element(by.css('span.step2')).isDisplayed().then(function (val) {
                    return val;
                })

            }, 3000, 'A long waiting for step2, chrome')

            // next request is xSetServer/ClientStatus
            browser.executeScript(function() {
                var guid = angular.element(document.getElementById("index_ctrl")).scope().challenge.guid;

                angular.element(document.getElementById("index_ctrl")).scope().xSetClientStatus(
                    {"challenge":guid,"type":"p2p","result":"SuCceSs"}
                );
            });

            // waiting...
            pr.wait(function() {
                return element(by.css('span.step4')).isDisplayed().then(function (val) {
                    return val;
                })

            }, 8000, 'A long waiting for step4 - playing, chrome')

        }
    })

    it('pause (from firefox - challenger)', function () {
        if (browserType == 'firefox') {
            browser.executeScript(function () {
                angular.element(document.getElementById("index_ctrl")).scope().xPause();
            });

            expect(element(by.css('div.owner_pause')).isDisplayed()).toBe(true);

            browser.executeScript(function () {
                angular.element(document.getElementById("index_ctrl")).scope().xResume();
            });

            expect(element(by.css('span.step4')).isDisplayed()).toBe(true);
        }

    });


    it('winner and looser results', function(){
        if (browserType == 'firefox') {
                browser.executeScript(function () {
                    var guid = angular.element(document.getElementById("index_ctrl")).scope().challenge.guid;
                    angular.element(document.getElementById("index_ctrl")).scope().xGameOver(guid, 28);
                });
        }
    });


});