import Converter from '../../src/Util/Converter'



describe('Logging into the system', () => {
    // define variables that we need on multiple occasions
    let uid // user id
    let email // email of the user


    before(function () {
        cy.clearCookies()
            .clearLocalStorage();

        return cy
            // Create user
            .fixture('user.json')
            .then((user) => {
                return cy.request({
                    method: 'POST',
                    url: 'http://localhost:5000/users/create',
                    form: true,
                    body: user,
                });
            })
            .then((response) => {
                uid = response.body._id.$oid;
                name = `${response.body.firstName} ${response.body.lastName}`;
                email = response.body.email;
            })

            // Create tasks and todos
            .then(() => cy.fixture('task.json'))
            .then((task) => {
                const data = new URLSearchParams();
                data.append('title', task.title);
                data.append('description', task.description);
                data.append('start', task.startdate);
                data.append('due', task.startdate);
                data.append('url', task.url);
                data.append('userid', uid);
                task.todos.forEach((todo) => data.append('todos', todo.description));

                return cy.request({
                    method: 'POST',
                    url: 'http://localhost:5000/tasks/create',
                    body: data.toString(),
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                });
            })


            // Set first todo to done
            .then(() => cy.request(`http://localhost:5000/tasks/ofuser/${uid}`))
            .then((response) => {
                const task_id = response.body[0]._id?.['$oid'];
                return cy.request(`http://localhost:5000/tasks/byid/${task_id}`);
            })
            .then((response) => {
                const converted = Converter.convertTask(response.body);
                const todoId = converted.todos[0]._id;
                const upd = new URLSearchParams();
                upd.append('data', JSON.stringify({ $set: { done: true } }));

                return cy.request({
                    method: 'PUT',
                    url: `http://localhost:5000/todos/byid/${todoId}`,
                    body: upd.toString(),
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                });
            });
    });


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
        cy.get('input[type=text][placeholder="Add a new todo item"]').type('Test Todo')
        cy.get('input[type=submit][value="Add"]')
            .click()

        cy.wait(2000)

        cy.get('ul.todo-list li')
            .eq(-2)
            .should('contain.text', 'Test Todo')
    })

    it('strikes through the first unchecked todo when clicked', () => {
        cy.get('ul.todo-list .checker.unchecked')
            .first()
            .click()
            .closest('li')
            .find('span.editable')
            .should('have.css', 'text-decoration')
            .and('contain', 'line-through')
    });

    it('removes strike through the first checked todo when clicked', () => {
        cy.get('ul.todo-list .checker.checked')
            .first()
            .click()
            .closest('li')
            .find('span.editable')
            .should('have.css', 'text-decoration')
            .and('contain', 'none')
    });

    it('removes a todo item when its remove button is clicked', () => {
        cy.get('ul.todo-list li')
            .first()
            .as('toDelete')
            .within(() => {
                cy.get('.remover').click();
            });
        cy.get('@toDelete').should('not.exist');
    });


    after(function () {
        //delete tasks and todos
        cy.request(`http://localhost:5000/tasks/ofuser/${uid}`)
            .then((response) => {
                const tasks = response.body;
                for (const task of tasks) {
                    const id = task._id?.['$oid'];

                    fetch(`http://localhost:5000/tasks/byid/${id}`, {
                        method: 'get',
                        headers: { 'Cache-Control': 'no-cache' }
                    })
                        .then(res => res.json())
                        .then(tobj => {
                            let converted = Converter.convertTask(tobj);
                            for (let todo of converted.todos) {

                                fetch(`http://localhost:5000/todos/byid/${todo._id}`, {
                                    method: 'delete',
                                    headers: { 'Cache-Control': 'no-cache' }
                                })
                            }
                        })
                        .catch(function (error) {
                            console.error(error)
                        })

                    if (id) {
                        cy.request({
                            method: 'DELETE',
                            url: `http://localhost:5000/tasks/byid/${id}`
                        }).then(() => cy.log(`Deleted task ${id}`));
                    }
                }
            });
        // clean up by deleting the user from the database
        cy.wait(2000)

        cy.request({
            method: 'DELETE',
            url: `http://localhost:5000/users/${uid}`
        }).then((response) => {
            cy.log(response.body)
        })
    })
})