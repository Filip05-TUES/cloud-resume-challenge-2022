const API_URL = Cypress.env('apiUrl');

describe('API Smoke Test', () => {

  it('GET request should return a valid count', () => {
    cy.request({
      method: 'GET',
      url: API_URL,
    }).then((response) => {
      expect(response.status).to.eq(200);
      const count = parseInt(response.body, 10);
      expect(count).to.be.a('number');
      expect(count).to.be.at.least(0);
    });
  });

  it('POST request should increment the database count', () => {
    let initialCount;
    let newCount;
    cy.request({
      method: 'GET',
      url: API_URL,
    }).then((response) => {
      expect(response.status).to.eq(200);
      initialCount = parseInt(response.body, 10);
      cy.log(`Initial count: ${initialCount}`);
      expect(initialCount).to.be.a('number');
    })
    .then(() => {
      cy.request({
        method: 'POST',
        url: API_URL,
      }).then((response) => {
        expect(response.status).to.eq(200);
        newCount = parseInt(response.body, 10);
        cy.log(`New count: ${newCount}`);
        expect(newCount).to.eq(initialCount + 1);
      });
    })
    .then(() => {
      cy.request({
        method: 'GET',
        url: API_URL,
      }).then((response) => {
        expect(response.status).to.eq(200);
        const updatedCount = parseInt(response.body, 10);
        cy.log(`Updated count: ${updatedCount}`);
        expect(updatedCount).to.eq(newCount);
      });
    });
  });

  it('Block unwanted requests', () => {
    cy.request({
      method: 'PUT',
      url: API_URL,
      failOnStatusCode: false,
    }).then((response) => {
      expect(response.status).to.eq(403);
    });
    cy.request({
      method: 'DELETE',
      url: API_URL,
      failOnStatusCode: false,
    }).then((response) => {
      expect(response.status).to.eq(403);
    });
  });
});