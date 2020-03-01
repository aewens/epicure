export const state = () => ({
    dbs: {},
    schemas: {},
});

export const mutations = {
    ADD_DATABASE(state, [ name, entries ]) {
        console.log("ADD_DATABASE", name, entries);
        state.dbs = { ...state.dbs, [name]: entries };
    },

    ADD_SCHEMA(state, [ name, schema ]) {
        console.log("ADD_SCHEMA", name, schema);
        state.schemas = { ...state.schemas, [name]: schema };
    }
};
