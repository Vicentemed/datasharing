document.addEventListener('DOMContentLoaded', () => {
    const loginContainer = document.getElementById('login-container');
    const mainContainer = document.getElementById('main-container');
    const loginForm = document.getElementById('login-form');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const logoutButton = document.getElementById('logout-button');
    const patientsContainer = document.getElementById('patients-container');
    const patientsList = document.getElementById('patients-list');
    const addPatientForm = document.getElementById('add-patient-form');
    const patientNameInput = document.getElementById('patient-name');
    const patientDobInput = document.getElementById('patient-dob');
    const chartsContainer = document.getElementById('charts-container');
    const patientNameHeader = document.getElementById('patient-name-header');
    const chartsList = document.getElementById('charts-list');
    const addChartForm = document.getElementById('add-chart-form');
    const chartDataInput = document.getElementById('chart-data');

    let token = null;
    let currentPatientId = null;

    // --- API Functions ---

    const api = {
        login: async (email, password) => {
            const response = await fetch('/dentists/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Basic ' + btoa(email + ':' + password)
                }
            });
            return response.json();
        },
        getPatients: async () => {
            const response = await fetch('/patients', {
                headers: { 'x-access-token': token }
            });
            return response.json();
        },
        addPatient: async (name, dateOfBirth) => {
            const response = await fetch('/patients', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'x-access-token': token
                },
                body: JSON.stringify({ name, date_of_birth: dateOfBirth })
            });
            return response.json();
        },
        getCharts: async (patientId) => {
            const response = await fetch(`/patients/${patientId}/charts`, {
                headers: { 'x-access-token': token }
            });
            return response.json();
        },
        addChart: async (patientId, chartData) => {
            const response = await fetch(`/patients/${patientId}/charts`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'x-access-token': token
                },
                body: JSON.stringify({ chart_data: chartData })
            });
            return response.json();
        }
    };

    // --- UI Functions ---

    const showLogin = () => {
        loginContainer.style.display = 'block';
        mainContainer.style.display = 'none';
    };

    const showMain = () => {
        loginContainer.style.display = 'none';
        mainContainer.style.display = 'block';
        chartsContainer.style.display = 'none';
        loadPatients();
    };

    const loadPatients = async () => {
        const patients = await api.getPatients();
        patientsList.innerHTML = '';
        patients.forEach(patient => {
            const li = document.createElement('li');
            li.textContent = `${patient.name} (${patient.date_of_birth})`;
            li.addEventListener('click', () => showCharts(patient));
            patientsList.appendChild(li);
        });
    };

    const showCharts = async (patient) => {
        currentPatientId = patient.id;
        patientNameHeader.textContent = `Charts for ${patient.name}`;
        chartsContainer.style.display = 'block';
        const charts = await api.getCharts(patient.id);
        chartsList.innerHTML = '';
        charts.forEach(chart => {
            const li = document.createElement('li');
            li.textContent = chart.chart_data;
            chartsList.appendChild(li);
        });
    };

    // --- Event Listeners ---

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = emailInput.value;
        const password = passwordInput.value;
        const data = await api.login(email, password);
        if (data.token) {
            token = data.token;
            showMain();
        } else {
            alert('Login failed');
        }
    });

    logoutButton.addEventListener('click', () => {
        token = null;
        showLogin();
    });

    addPatientForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = patientNameInput.value;
        const dob = patientDobInput.value;
        await api.addPatient(name, dob);
        loadPatients();
        addPatientForm.reset();
    });

    addChartForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const chartData = chartDataInput.value;
        await api.addChart(currentPatientId, chartData);
        showCharts({ id: currentPatientId, name: patientNameHeader.textContent.replace('Charts for ', '') });
        addChartForm.reset();
    });

    // --- Initial State ---

    showLogin();
});
