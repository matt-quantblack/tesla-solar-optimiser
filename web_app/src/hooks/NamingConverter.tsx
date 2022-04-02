export function keysToCamel(o: any): any {

    function toCamel(s: string): any {
        return s.replace(/([-_][a-z])/gi, ($1: any) => {
            return $1.toUpperCase().replace('-', '').replace('_', '');
        });
    }


    if (o === Object(o) && !Array.isArray(o) && typeof o !== 'function') {
        const n: any = {};
        Object.keys(o).forEach((k: string) => {
            n[toCamel(k)] = keysToCamel(o[k]);
        });
        return n;
    } else if (Array.isArray(o)) {
        return o.map((i) => {
        return keysToCamel(i);
        });
    }
    return o;
};

export function keysToSnake(o: any): any {

    function toSnake(s: string): any {
        return s.replace(/[A-Z]/g, (letter: string) => `_${letter.toLowerCase()}`);
        }
        
    if (o === Object(o) && !Array.isArray(o) && typeof o !== 'function') {
        const n: any = {};
        Object.keys(o).forEach((k: string) => {
            n[toSnake(k)] = keysToSnake(o[k]);
        });
        return n;
    } else if (Array.isArray(o)) {
        return o.map((i) => {
        return keysToSnake(i);
        });
    }
    return o;
};

  

  