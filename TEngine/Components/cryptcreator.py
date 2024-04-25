# must install cryptography
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import BestAvailableEncryption, Encoding, PrivateFormat, NoEncryption
from cryptography.hazmat.backends import default_backend
from cryptography.x509.oid import ExtensionOID
import typing as T
import datetime

from ..interfaces import CryptCreator as ICryptCreator

class CryptCreator(ICryptCreator):
    def __init__(
        self,
        country         : str       = u"US",
        state           : str       = u"California",
        locality        : str       = u"San Francisco",
        organization    : str       = u"TEngine",
        organizationUnit: str       = u"TEngine",
        commonName      : str       = u"localhost",
        email           : str       = u"admin@localhost",
        keySize         : int       = 2048,
        password        : str       = None,
        public_exponent : int       = 65537,
        backend         = default_backend(),
        serial_number   : T.Optional[int]= None,
        valid_before    : T.Optional[datetime.datetime] = None,
        valid_after     : T.Optional[datetime.datetime] = None,
        not_valid_before: T.Optional[datetime.datetime] = None,
        not_valid_after : T.Optional[datetime.datetime] = None,
        extension       : T.Optional[x509.Extension] = None
    ) -> None:
        self.country = country
        self.state = state
        self.locality = locality
        self.organization = organization
        self.organizationUnit = organizationUnit
        self.commonName = commonName
        self.email = email
        self.keySize = keySize
        self.password = password
        self.public_exponent = public_exponent
        self.backend = backend
        self.serial_number = serial_number
        self.valid_before = valid_before
        self.valid_after = valid_after
        self.not_valid_before = not_valid_before
        self.not_valid_after = not_valid_after
        if extension is None:
            self.extension = x509.SubjectAlternativeName([x509.DNSName(commonName)])
        else:
            self.extension = extension
        return
    
    def sign(self) -> None:
        """生成RSA私钥和自签名证书。证书将使用实例变量中的配置参数。"""
        self.private_key = rsa.generate_private_key(
            public_exponent=self.public_exponent,
            key_size=self.keySize,
            backend=self.backend
        )
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, self.country),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, self.state),
            x509.NameAttribute(NameOID.LOCALITY_NAME, self.locality),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, self.organization),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, self.organizationUnit),
            x509.NameAttribute(NameOID.COMMON_NAME, self.commonName),
            x509.NameAttribute(NameOID.EMAIL_ADDRESS, self.email),
        ])
        self.cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            self.private_key.public_key()
        ).serial_number(
            self.serial_number if self.serial_number else x509.random_serial_number()
        ).not_valid_before(
            self.not_valid_before if self.not_valid_before else datetime.datetime.utcnow()
        ).not_valid_after(
            self.not_valid_after if self.not_valid_after else datetime.datetime.utcnow() + datetime.timedelta(days=365)
        ).add_extension(
            self.extension,
            critical=False,
        ).sign(self.private_key, hashes.SHA256(), self.backend)

    def write( self, certfile: str, keyfile: str ) -> None:
        """将生成的私钥和证书写入到指定的文件中。

        参数:
            certfile: 证书文件的路径。
            keyfile: 私钥文件的路径。
        """
        with open( keyfile, "wb" ) as fp:
            fp.write(
                self.private_key.private_bytes(
                    encoding=Encoding.PEM,
                    format=PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=NoEncryption() if self.password is None else BestAvailableEncryption(self.password)
                )
            )
        with open( certfile, "wb" ) as fp:
            fp.write( self.cert.public_bytes(Encoding.PEM) )
    