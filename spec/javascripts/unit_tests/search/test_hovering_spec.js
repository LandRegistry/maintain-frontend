describe('Highlighting elements', function() {
    var planningCharge, housingCharge;

    beforeEach(function () {
        ko.cleanNode($('body')[0]);
        search.searchViewModel = new search.SearchViewModel()

        var item = {
            'display_id': 'LLC-FCDQF',
            'geometry': {features: [], type: "FeatureCollection"},
            'item': {
                'charge-type': 'Planning',
                'further-information-reference': 'PLA/220023'
            }
        };

        planningCharge = new search.Charge(item)

        item = {
            'display_id': 'LLC-34RT',
            'geometry': {features: [], type: "FeatureCollection"},
            'item': {
                'charge-type': 'Housing',
                'further-information-reference': 'PLA/220023'
            }
        };

        housingCharge = new search.Charge(item)
        search.searchViewModel.setCategoryCharges([planningCharge, housingCharge])
    });

    describe('on hovering over a charge in sidebar', function() {
        var featureSpy;

        beforeEach(function() {
            featureSpy = jasmine.createSpyObj('feature', {
                'getProperties': {'charge': planningCharge},
                'setStyle': {},
                'getGeometry': jasmine.createSpyObj('geometry', {'getType': 'Polygon'})
            });

            spyOn(search.highlightedSource, 'addFeature');
            spyOn(search.highlightedSource, 'removeFeature');
            spyOn(planningCharge, 'getFeatures').and.returnValue([featureSpy]);


            setFixtures('<ul class="list"> <li id="LLC-FCDQF"> </li> </ul>');
        });

        it('is highlighted', function() {
            spyOn(featureHelpers, 'addFeaturesToSource');

            planningCharge.highlight();

            expect($("#" + planningCharge.id).hasClass('highlighted')).toEqual(true);
            expect(featureSpy.setStyle).toHaveBeenCalledTimes(1);
            expect(featureSpy.setStyle).toHaveBeenCalledWith(llc_layer_styles.selected_style['Polygon']);
            expect(featureHelpers.addFeaturesToSource).toHaveBeenCalled()
        });

        it('removes highlight', function() {
            spyOn(featureHelpers, 'removeFeaturesFromSource');

            planningCharge.removeHighlight();

            expect($("#" + planningCharge.id).hasClass('highlighted')).toEqual(false);
            expect(featureSpy.setStyle).toHaveBeenCalledTimes(1);
            expect(featureSpy.setStyle).toHaveBeenCalledWith(llc_layer_styles.standard_style['Polygon']);
            expect(featureSpy.setStyle).toHaveBeenCalledWith(llc_layer_styles.standard_style['Polygon']);
            expect(featureHelpers.removeFeaturesFromSource).toHaveBeenCalled()
        });
    });

    describe('on setting highlightedFeature', function() {
        var planningCategory, housingCategory;
        var planningSpy, housingSpy;
        beforeEach(function() {
            spyOn(MAP_HELPERS, 'init_controls').and.callFake(function() {})

            planningCategory = planningCharge.category
            housingCategory = housingCharge.category

            planningSpy = jasmine.createSpyObj('planningFeature', {'getProperties': {'charge': planningCharge}});
            housingSpy = jasmine.createSpyObj('housingFeature', {'getProperties': {'charge': housingCharge}});

            setFixtures('<div id="full-screen-map-sidebar">' +
                '<div id="' + planningCategory.sectionId() + '" class="accordion-section">' +
                '<div class="accordion-section-header">' +
                '<ul class="list"><li id=' + planningCharge.id + '></li></ul>' +
                '</div></div>' +
                '<div id="' + housingCategory.sectionId() + '" class="accordion-section">' +
                '<div class="accordion-section-header">' +
                '<ul class="list"><li id=' + housingCharge.id + '></li></ul>' +
                '</div></div></div>');

            search.init([], '');
        });

        it('highlighting on accordion header, remove from old charge and added to new', function() {
            planningCategory.expanded = false
            housingCategory.expanded = false

            spyOn(search, 'scrollTo')
            search.searchViewModel.highlightedFeature(planningSpy);

            expect($("#" + planningCategory.sectionId() + " .accordion-section-header").hasClass('highlighted')).toEqual(true);

            search.searchViewModel.highlightedFeature(housingSpy)

            expect($("#" + planningCategory.sectionId() + " .accordion-section-header").hasClass('highlighted')).toEqual(false);
            expect($("#" + housingCategory.sectionId() + " .accordion-section-header").hasClass('highlighted')).toEqual(true);
        });

        it('highlighting on accordion row, remove from old charge and added to new', function() {
            planningCategory.expanded = true
            housingCategory.expanded = true

            spyOn(search, 'scrollTo')

            search.searchViewModel.highlightedFeature(planningSpy);

            expect($("#" + planningCharge.id).hasClass('highlighted')).toEqual(true);

            search.searchViewModel.highlightedFeature(housingSpy)

            expect($("#" + planningCharge.id).hasClass('highlighted')).toEqual(false);
            expect($("#" + housingCharge.id).hasClass('highlighted')).toEqual(true);
        });

        it('highlighting on accordion header and row, remove from old charge and added to new', function() {
            planningCategory.expanded = true
            housingCategory.expanded = false

            spyOn(search, 'scrollTo')

            search.searchViewModel.highlightedFeature(planningSpy);

            expect($("#" + planningCharge.id).hasClass('highlighted')).toEqual(true);

            search.searchViewModel.highlightedFeature(housingSpy)

            expect($("#" + planningCharge.id).hasClass('highlighted')).toEqual(false);
            expect($("#" + housingCategory.sectionId() + " .accordion-section-header").hasClass('highlighted')).toEqual(true);
        });
    })
});
