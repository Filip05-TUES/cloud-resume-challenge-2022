const API_URL = Cypress.env('apiUrl'); 
const checkApiStatus = (req) => {
    req.continue((res) => {
        if (res.statusCode >= 400) {
            cy.log(`***API FAILED with status: ${res.statusCode}***`);
            cy.log(`***API FAILED with body: ${JSON.stringify(res.body)}***`); 
            throw new Error(`API POST failed with status ${res.statusCode}. Check CI logs for details.`); 
        }
    });
};

describe('Resume Website E2E Test', () => {

    const VISITOR_COUNT_SELECTOR = '#visitor-count';
    const NUMBER_REGEX = /(\d+)/; 
    const TIMEOUT = 10000;

    beforeEach(() => {
        cy.clearLocalStorage();
        cy.intercept('POST', API_URL, checkApiStatus).as('updateVisitorCount');
        cy.intercept('GET', API_URL).as('getVisitorCount');
        cy.visit('/');
        cy.wait('@updateVisitorCount', { timeout: TIMEOUT });
    });

    it('should load the resume and verify static content exists', () => {
        cy.contains('Filip Ermenkov');
        cy.get(VISITOR_COUNT_SELECTOR)
          .should('be.visible')
          .should('contain', 'Visitors');
    });

    it('should display a valid numerical visitor count from the API', () => {
        cy.get(VISITOR_COUNT_SELECTOR, { timeout: TIMEOUT })
          .should('be.visible')
          .invoke('text')
          .then((text) => {
            const match = text.match(NUMBER_REGEX);
            const count = match ? parseInt(match[0], 10) : NaN;

            expect(count).to.be.a('number');
            expect(count).to.be.at.least(1);
            cy.log(`Successfully displayed count: ${count}`);
          });
    });

    it('should increment the visitor count when visited by a new "user"', () => {
        let firstCount;

        cy.get(VISITOR_COUNT_SELECTOR, { timeout: TIMEOUT })
          .invoke('text')
          .then((text) => {
            const match = text.match(NUMBER_REGEX);
            firstCount = match ? parseInt(match[0], 10) : NaN;
            cy.log(`Count after first visit (N): ${firstCount}`);
          });

        cy.clearLocalStorage();
        cy.intercept('POST', API_URL, checkApiStatus).as('secondUpdateVisitorCount');
        cy.visit('/');

        cy.wait('@secondUpdateVisitorCount', { timeout: TIMEOUT });

        cy.get(VISITOR_COUNT_SELECTOR, { timeout: TIMEOUT })
          .invoke('text')
          .then((text) => {
            const match = text.match(NUMBER_REGEX);
            const secondCount = match ? parseInt(match[0], 10) : NaN;
            cy.log(`Count after second visit (N+1): ${secondCount}`);

            expect(secondCount).to.eq(firstCount + 1);
          });
    });

    it('should keep the visitor count the same on a simple page reload', () => {
        let firstCount;

        cy.get(VISITOR_COUNT_SELECTOR, { timeout: TIMEOUT })
          .invoke('text')
          .then((text) => {
            const match = text.match(NUMBER_REGEX);
            firstCount = match ? parseInt(match[0], 10) : NaN;
            cy.log(`Count before reload (N): ${firstCount}`);
          });

        cy.reload(); 

        cy.wait('@getVisitorCount', { timeout: TIMEOUT });

        cy.get(VISITOR_COUNT_SELECTOR, { timeout: TIMEOUT })
          .invoke('text')
          .then((text) => {
            const match = text.match(NUMBER_REGEX);
            const secondCount = match ? parseInt(match[0], 10) : NaN;
            cy.log(`Count after reload (Still N): ${secondCount}`);

            expect(secondCount).to.eq(firstCount);
          });
    });
});