describe('Logging into the system', () => {
    // define variables that we need on multiple occasions
    let uid // user id
    let name // name of the user (firstName + ' ' + lastName)
    let email // email of the user
    let title
    let description
    let task_id
    let todos

    before(function () {
        cy.clearCookies();
        cy.clearLocalStorage();

        cy.fixture('user.json')
            .then((user) => {
                cy.request({
                    method: 'POST',
                    url: 'http://localhost:5000/users/create',
                    form: true,
                    body: user
                }).then((response) => {
                    uid = response.body._id.$oid
                    name = user.firstName + ' ' + user.lastName
                    email = user.email
                })
            })

        cy.fixture('task.json').then((task) => {
            const data = new URLSearchParams();

            data.append('title', task.title);
            data.append('description', task.description);
            data.append('start', task.startdate);
            data.append('due', task.startdate);
            data.append('url', task.url);
            data.append('userid', uid);

            // Send todo descriptions only — same as working example
            for (const todo of task.todos) {
                data.append('todos', todo.description);
            }

            cy.request({
                method: 'POST',
                url: 'http://localhost:5000/tasks/create',
                body: data.toString(),
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                }
            }).then((response) => {
                task_id = response.body
            });
        });


    })

    beforeEach(function () {
        // enter the main main page
        cy.visit('http://localhost:3000')
        cy.contains('div', 'Email Address')
            .find('input[type=text]')
            .type(email)
        // submit the form on this page
        cy.get('form')
            .submit()
        cy.get(".container-element > a", { timeout: 10000 }).click({ force: true })
        cy.viewport(1280, 1200)

    })

    it('checks that add button is not enabled when no description field data', () => {
        // make sure that Add button is not clickable if nothing in description field
        cy.get('input[type=submit][value="Add"]').scrollIntoView().should('be.disabled');
    })

    it('checks that add button is enabled when description field has data', () => {
        // make sure that Add button is clickable if something is in description field
        cy.get('input[type=text][placeholder="Add a new todo item"]').type('Test Todo')
        cy.get('input[type=submit][value="Add"]').scrollIntoView().should('be.not.disabled');
    })

    it('presses add todo when description field has no data', () => {
        // should not add a new todo when description field is empty
        cy.get('ul.todo-list li')
            .its('length')
            .then(initialCount => {
                // cy.task('log', `Initial count: ${initialCount}`)
                cy.get('input[type=submit][value="Add"]')
                    .click()

                cy.wait(2000)

                cy.get('ul.todo-list li')
                    .its('length')
                    .then(newCount => {
                        // cy.task('log', `New count: ${newCount}`)
                        cy.wrap(newCount).should('equal', initialCount)
                    })
            })
    })



    it('adds a new todo at the last position when description field has data and add button is pressed', () => {
        // cy.task('log', `Initial count: ${initialCount}`)
        cy.get('input[type=text][placeholder="Add a new todo item"]').type('Test Toda')
        cy.get('input[type=submit][value="Add"]')
            .click()

        cy.wait(2000)

        cy.get('ul.todo-list li')
            .eq(-2)
            .should('contain.text', 'Test Todo')
    })

    after(function () {
        cy.request(`http://localhost:5000/tasks/ofuser/${uid}`).then((response) => {
            const tasks = response.body;
            for (const task of tasks) {
                const id = task._id?.['$oid'];
                if (id) {
                    cy.request({
                        method: 'DELETE',
                        url: `http://localhost:5000/tasks/byid/${id}`
                    }).then(() => cy.log(`Deleted task ${id}`));
                }
            }
        });
        // clean up by deleting the user from the database
        cy.request({
            method: 'DELETE',
            url: `http://localhost:5000/users/${uid}`
        }).then((response) => {
            cy.log(response.body)
        })
    })
})