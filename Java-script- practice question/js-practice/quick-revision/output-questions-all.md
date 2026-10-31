# Output Questions Q001–Q050
# Quick Revision Cheatsheet (Node.js CommonJS outputs)

---

## 🪝 Hoisting (Q001–Q005)

```javascript
// Q001: var hoisting
console.log(a); var a = 5; console.log(a);
// Output: undefined, 5 (declaration hoisted, value NOT)

// Q002: let TDZ
console.log(a); let a = 5;
// Output: ReferenceError (Cannot access 'a' before initialization)

// Q003: const TDZ
try { console.log(PI); } catch (e) { console.log(e.name); }
const PI = 3.14; console.log(PI);
// Output: ReferenceError, 3.14

// Q004: function declaration vs expression
console.log(greet()); function greet() { return 'Hello'; }
console.log(typeof expr);
try { expr(); } catch (e) { console.log(e.name); }
var expr = function () {};
// Output: Hello, undefined, TypeError (declaration fully hoisted; var expr = undefined)

// Q005: mixed hoisting
console.log(a); console.log(typeof foo); console.log(typeof bar);
var a = 1; function foo() {} var foo = 5; var bar = function () {};
console.log(foo);
try { console.log(c); } catch (e) { console.log(e.name); }
let c = 3;
// Output: undefined, function, undefined, 5, ReferenceError
```

---

## 🔁 Closures + Timers (Q006–Q010)

```javascript
// Q006: var loop + setTimeout
for (var i = 0; i < 3; i++) setTimeout(function () { console.log(i); }, 1000);
// Output: 3, 3, 3 (ek hi shared var i)

// Q007: let loop closure
const fns = [];
for (let i = 0; i < 3; i++) fns.push(() => i);
console.log(fns.map(f => f()));
// Output: [ 0, 1, 2 ] (let = har iteration ka naya binding)

// Q008: setTimeout sees latest value
function outer() { let count = 0; setTimeout(() => console.log('timeout', count), 0); count++; count++; }
outer(); console.log('sync');
// Output: sync, timeout 2 (closure variable ko hold karta hai, snapshot nahi)

// Q009: var + delay i*10
for (var i = 0; i < 3; i++) setTimeout(() => console.log(i), i * 10);
// Output: 3, 3, 3

// Q010: let + delay (3-i)*10
for (let i = 0; i < 3; i++) setTimeout(() => console.log(i), (3 - i) * 10);
// Output: 2, 1, 0 (chhota delay pehle fire hota hai)
```

---

## ⏱️ Event Loop (Q011–Q017)

```javascript
// Q011: sync → microtask → macrotask
console.log('1'); setTimeout(() => console.log('2'), 0);
Promise.resolve().then(() => console.log('3')); console.log('4');
// Output: 1, 4, 3, 2

// Q012: async/await — code before await is sync
async function main() { console.log('1'); await Promise.resolve(); console.log('2'); }
console.log('3'); main(); console.log('4');
// Output: 3, 1, 4, 2

// Q013: promise + nested timeout
console.log('A'); setTimeout(() => console.log('B'), 0);
Promise.resolve().then(() => { console.log('C'); setTimeout(() => console.log('D'), 0); }).then(() => console.log('E'));
setTimeout(() => console.log('F'), 0); console.log('G');
// Output: A, G, C, E, B, F, D (D baad me schedule hua, isliye last)

// Q014: nextTick beats promise
console.log('start'); setTimeout(() => console.log('timeout'), 0);
Promise.resolve().then(() => console.log('promise'));
process.nextTick(() => console.log('nextTick')); console.log('end');
// Output: start, end, nextTick, promise, timeout

// Q015: inside I/O callback
fs.readFile(__filename, () => {
  setTimeout(() => console.log('timeout'), 0); setImmediate(() => console.log('immediate'));
});
// Output: immediate, timeout (I/O ke andar setImmediate hamesha pehle)

// Q016: microtasks drain fully before macrotasks
setTimeout(() => console.log('macro 1'), 0); setTimeout(() => console.log('macro 2'), 0);
queueMicrotask(() => { console.log('micro 1'); queueMicrotask(() => console.log('micro 3')); });
queueMicrotask(() => console.log('micro 2')); console.log('sync');
// Output: sync, micro 1, micro 2, micro 3, macro 1, macro 2

// Q017: everything mixed
console.log('1'); setTimeout(() => console.log('2'), 0);
new Promise(res => { console.log('3'); res(); }).then(() => console.log('4'));
(async () => { console.log('5'); await null; console.log('6'); })();
process.nextTick(() => console.log('7')); console.log('8');
// Output: 1, 3, 5, 8, 7, 4, 6, 2
```

---

## 🎯 this Binding (Q018–Q023)

```javascript
// Q018: lost this
const obj = { name: 'Arjun', greet: function () { console.log(this.name); } };
obj.greet(); const fn = obj.greet; fn();
// Output: Arjun, undefined (Node non-strict); strict me TypeError

// Q019: arrow this (module scope)
const o = { name: 'Aditya', regular() { return this.name; },
  arrow: () => this === module.exports, nested() { const inner = () => this.name; return inner(); } };
// o.regular() → Aditya | o.arrow() → true | o.nested() → Aditya

// Q020: class method detached
const b = new Btn();  // click() { return this.label; }
b.click();            // OK
const f = b.click; f();
// Output: OK, TypeError (class body strict hai → this undefined)

// Q021: this in setTimeout (Node)
run() {
  setTimeout(function () { console.log(this.name); }, 0);       // undefined (this = Timeout obj)
  setTimeout(() => console.log(this.name), 0);                  // A
  setTimeout(function () { console.log(this.name); }.bind(this), 0); // A
}
// Output: undefined, A, A

// Q022: EventEmitter listener
em.on('x', function () { console.log(this === em, this.id); });
em.on('x', () => console.log(this === em));
em.emit('x');
// Output: true emitter, false (arrow ka this module scope hota hai)

// Q023: call / apply / bind
function intro(g, p) { return `${g}, ${this.name}${p}`; } const u = { name: 'Ravi' };
intro.call(u, 'Hi', '!');          // Hi, Ravi!
intro.apply(u, ['Hello', '?']);    // Hello, Ravi?
const bd = intro.bind(u, 'Hey'); bd('.');  // Hey, Ravi.
bd.call({ name: 'Other' }, '!');   // Hey, Ravi!  (bind permanent hai, call override nahi karta)
```

---

## 🧬 Prototype / instanceof / typeof (Q024–Q026)

```javascript
// Q024: prototype chain
function Animal() {} Animal.prototype.speak = function () { return 'sound'; };
function Dog() {} Dog.prototype = Object.create(Animal.prototype); Dog.prototype.constructor = Dog;
const d = new Dog();
d.speak();                                  // sound
d.hasOwnProperty('speak');                  // false (prototype se aaya)
Object.getPrototypeOf(d) === Dog.prototype; // true
Object.getPrototypeOf(Object.prototype);    // null (chain ka end)

// Q025: instanceof
class A {} class B extends A {} const bb = new B();
// bb instanceof B, A, Object → true true true
// 'str' instanceof String → false | new String('s') instanceof String → true
// Object.create(null) instanceof Object → false

// Q026: typeof traps
typeof null;          // 'object' (famous bug)
typeof NaN;           // 'number'
typeof [];            // 'object'
typeof function(){};  // 'function'
typeof undeclaredVar; // 'undefined' (no error)
```

---

## ⚖️ Equality & NaN (Q027–Q029)

```javascript
// Q027: == vs ===
0 == false;          // true
0 === false;         // false
'' == false;         // true
null == undefined;   // true
null === undefined;  // false
NaN == NaN;          // false

// Q028: null vs undefined
null == undefined;   // true
null === undefined;  // false
null == 0;           // false (== me null sirf undefined ke barabar)
null >= 0;           // true  (>= me null → 0)

// Q029: NaN
NaN === NaN;            // false
NaN == NaN;             // false
Number.isNaN(NaN);      // true
isNaN('hello');         // true  (pehle Number('hello') = NaN)
Number.isNaN('hello');  // false (coerce nahi karta)
```

---

## 🔀 Type Coercion (Q030–Q035)

```javascript
// Q030: classic traps
1 + '2';     // '12'
'3' - 1;     // 2
true + true; // 2
[] + [];     // ''
[] + {};     // '[object Object]'
{} + [];     // '[object Object]' (console.log ke andar expression hai)
+'';         // 0
+null;       // 0
+undefined;  // NaN
+false;      // 0

// Q031: string + number
'5' + 3;     // '53'
'5' - 3;     // 2
1 + 2 + '3'; // '33' (left→right: 3 + '3')
'1' + 2 + 3; // '123'
'5' * '2';   // 10

// Q032: object + string
({a:1}) + 'x';              // '[object Object]x'
`${{a:1}}`;                 // '[object Object]'
[1, 2] + 'x';               // '1,2x'
({ toString() { return 'custom'; } }) + '!'; // 'custom!'

// Q033: array + array
[] + [];            // '' (empty line)
typeof ([] + []);   // 'string'
[1] + [2];          // '12'
[] + 1;             // '1'

// Q034: array + object
[] + {};                // '[object Object]'
typeof ([] + {});       // 'string'
[] + {} + 1;            // '[object Object]1'
[1, 2] + {};            // '1,2[object Object]'

// Q035: {} + [] — statement vs expression
console.log({} + []);     // [object Object]
console.log(({}) + []);   // [object Object]
const x = {} + []; console.log(x); // [object Object]
eval('{} + []');          // 0 (statement position: {} = empty block, +[] = 0)
```

---

## ✅ Truthy / Short-circuit / Nullish / Optional (Q036–Q039)

```javascript
// Q036: truthy / falsy
// [0, '', '0', [], {}, null, undefined, NaN, -1, ' ']
// Output: falsy, falsy, truthy, truthy, truthy, falsy, falsy, falsy, truthy, truthy
// Falsy list: false, 0, -0, 0n, '', null, undefined, NaN — baaki sab truthy

// Q037: short-circuit
0 || 'a';                   // 'a'
1 && 'b';                   // 'b'
null && console.log('never'); // null (right side run hi nahi hota)
'' || null || 0;            // 0 (sab falsy → last value)

// Q038: ??
null ?? 'default';          // 'default'
0 ?? 'default';             // 0
'' ?? 'default';            // '' (empty line)
undefined ?? null ?? 'last';// 'last'

// Q039: ?.
user.profile?.name;   // undefined (profile null)
user.address?.city;   // undefined
user.greet?.();       // 'hi'
user.missing?.();     // undefined (call skip)
user.tags?.[0];       // 'js'
```

---

## 📦 Spread / Rest / Destructuring / Defaults (Q040–Q043)

```javascript
// Q040: spread = shallow copy
const a = { x: 1, nested: { y: 2 } }; const b = { ...a, x: 9 }; b.nested.y = 99;
console.log(a.x, a.nested.y);                 // 1 99
console.log([...'hi'], [...[1, 2], ...[3]]);  // [ 'h', 'i' ] [ 1, 2, 3 ]

// Q041: rest param
function sum(first, ...rest) { console.log(first, rest, rest.length); }
sum(1, 2, 3, 4); // 1 [ 2, 3, 4 ] 3
sum(1);          // 1 [] 0
sum();           // undefined [] 0

// Q042: destructuring defaults
const { a1, b1 = 5, c: renamed = 7 } = { a1: 1, c: undefined };
const [x, , y = 3, ...z] = [10, 20, undefined, 40, 50];
// a1 b1 renamed → 1 5 7  |  x y z → 10 3 [ 40, 50 ]  (default sirf undefined pe lagta hai)

// Q043: default params
function f(a, b = a * 2, c = []) { c.push(a); return [a, b, c]; }
f(1);               // [ 1, 2, [ 1 ] ]
f(1, null);         // [ 1, null, [ 1 ] ]  (null ≠ undefined)
f(1, undefined, [0]); // [ 1, 2, [ 0, 1 ] ]
f(2);               // [ 2, 4, [ 2 ] ]  (har call pe naya [])
```

---

## 🧩 Generator / Symbol / Map / Set / WeakMap (Q044–Q048)

```javascript
// Q044: generator two-way
function* gen() { const x = yield 1; console.log('x =', x); const y = yield x * 2; return x + y; }
const g = gen();
g.next('ignored'); // { value: 1, done: false }  (pehle next ka arg ignore)
g.next(10);        // logs 'x = 10' → { value: 20, done: false }
g.next(5);         // { value: 15, done: true }
g.next();          // { value: undefined, done: true }

// Q045: Symbol
const s1 = Symbol('id'), s2 = Symbol('id'); const o2 = { [s1]: 1, name: 'A' };
s1 === s2;                       // false
Object.keys(o2);                 // [ 'name' ]
JSON.stringify(o2);              // {"name":"A"}
Symbol.for('k') === Symbol.for('k'); // true

// Q046: Map vs Object keys
obj[k1] = 'one'; obj[k2] = 'two';   // dono key '[object Object]' ban jaati hain
map.set(k1, 'one'); map.set(k2, 'two');
// Object.keys(obj).length, map.size → 1 2
// obj[k1], map.get(k1) → two one

// Q047: Set
new Set([1, 1, '1', NaN, NaN, {}, {}, [], []]).size; // 7  (1, '1', NaN, 2 objs, 2 arrays)
[...new Set('aabbc')].join('');                       // 'abc'

// Q048: WeakMap
wm.set(key, 'secret');
wm.get(key); wm.has(key); wm.has({ id: 1 }); // secret true false
wm.set('str', 1);                            // TypeError (key object honi chahiye)
wm.size;                                     // undefined (WeakMap me size nahi)
```

---

## 🔧 delete / in (Q049–Q050)

```javascript
// Q049: delete
delete obj.a;              // true → { b: 2 }
delete arr[1];             // arr = [ 1, <1 empty item>, 3 ], length 3 (hole bana, shift nahi)
var x = 10; delete x; x;   // false, 10 (var delete nahi hota)

// Q050: in operator
const o3 = { a: undefined };
'a' in o3;                   // true (key exist karti hai, value undefined)
'toString' in o3;            // true (prototype chain bhi check)
o3.hasOwnProperty('toString'); // false
2 in [10, 20, 30];           // true (index check, value nahi)
'length' in [];              // true
```
