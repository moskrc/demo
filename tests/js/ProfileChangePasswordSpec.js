describe('Unit: ProfileController Unit Tests', function () {
    beforeEach(module('main'));

    var ctrl, scope, currentUserService, timerCallback;

    var test_user = {'email': 'test@test.com', 'username': 'test'};

    beforeEach(inject(function ($injector, $controller, $rootScope) {

        $q = $injector.get('$q');
        $timeout = $injector.get('$timeout');
        $httpBackend = $injector.get('$httpBackend');

        timerCallback = jasmine.createSpy('timerCallback');

        jasmine.Clock.useMock();

        currentUserService = {
            'get': function (val) {
                var deferred = $q.defer();
                $timeout(function () {
                    timerCallback();
                    deferred.resolve(val(test_user));
                }, 3000);
                return deferred.promise;
            }
        }

        scope = $rootScope.$new();

        ctrl = $controller('ProfileChangePasswordController', {
            $scope: scope,
            CurrentUserService: currentUserService
        });

        $httpBackend.when('GET').respond(function () {
        });

    }));


    it('should have a var for current user, it\'s null',
        function () {
            expect(scope.user).toBeNull();
        });

    it('it should use an array for alerts',
        function () {
            expect(scope.alerts).toBeDefined();
        });

    it("will get an user later", function () {
        $timeout.flush();
        expect(scope.user).toEqual(test_user);
    });

});